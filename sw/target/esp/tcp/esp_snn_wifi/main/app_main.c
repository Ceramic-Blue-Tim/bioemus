/*
*! @title      Wifi spike monitoring
*! @file       app_main.cpp
*! @author     Romain Beaubois
*! @date       20 Apr 2023
*! @copyright
*! SPDX-FileCopyrightText: © 2023 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*! @brief
*! Wifi spike monitoring
*! * Wifi AP : esp as wifi access point
*! * SPI poll task : poll data from FPGA in SPI to get spikes
*! * TCP client task : send data via TCP
*! 
*! @details
*! > **20 Apr 2023** : file creation (RB)
*/

#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"

#include "esp_mac.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_spi_flash.h"
#include "esp_netif.h"
#include "esp_wifi_ap_get_sta_list.h"
#include "esp_intr_alloc.h"
#include "nvs_flash.h"
#include "soc/rtc_periph.h"
#include "driver/spi_slave.h"
#include "driver/gpio.h"

#include "lwip/sockets.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"
#include "lwip/igmp.h"
#include "lwip/err.h"
#include "lwip/sys.h"

/*----------------------
 |  Main parameters
 -----------------------*/
#define NB_FRAME_PER_BUFFER    100 // sending rate in ms

/*----------------------
 |  Configuration
 -----------------------*/

// Wifi Access Point configuration
#define ESP_WIFI_SSID           "snn_hh_spikes"
#define ESP_WIFI_PASS           "snn_hh_spikes"
#define ESP_WIFI_CHANNEL        1
#define ESP_WIFI_MAX_STA_CON    1

// TCP Server
#define TCP_SERVER_IP               "192.168.4.2"
#define TCP_SERVER_PORT             4444
#define TCP_CLIENT_MAX_CONNECT_TRY  32

// SPI
#define SPI_RX_BUFFER_COUNT     8
#define TSTAMP_BIT_SIZE         (32)
#define SPI_FRAME_BIT_SIZE      (512+TSTAMP_BIT_SIZE)   // Max size of frame is 64 bytes -> 512 bits
#define SPI_FRAME_BYTE_SIZE     (SPI_FRAME_BIT_SIZE/8)  // Max size of frame is 64 bytes -> 512 bits
#define TSTAMP_BYTE_SIZE        (TSTAMP_BIT_SIZE/8)

struct spi_dma_buffer_t {
    WORD_ALIGNED_ATTR unsigned char buf[SPI_FRAME_BYTE_SIZE];
};

#define SPI_FREQ        6250000 // Hz ==> 6.25 MHz  // 8800000 -> 8.8 MHz
#define GPIO_MOSI       23
#define GPIO_MISO       19
#define GPIO_SCLK       18
#define GPIO_CS         5
#define GPIO_HANDSHAKE  2 // (semaphore) input: ESP32 to FPGA
#define RCV_HOST        SPI3_HOST

// Task Priorities
#define SPI_POLL_TASK_PRIO      3
#define TCP_CLIENT_TASK_PRIO    2

// TCP task
#define TCP_BUFFER_BYTE_SIZE    (NB_FRAME_PER_BUFFER*SPI_FRAME_BYTE_SIZE)

// Queue
#define QUEUE_SPIKES_LENGTH 16

/*----------------------
 |  Logs
 -----------------------*/
static const char *TAG_AP           = "Wifi AP";
static const char *TAG_TCP_CLIENT   = "TCP Client task";
static const char *TAG_POLL_SPI     = "SPI Poll task";

#define ESP_WIFI_LOGS
#define TCP_SERVER_LOGS
// #define SPI_POLL_LOGS

/*----------------------
 |  Handlers
 -----------------------*/
QueueHandle_t queue_spikes;

/*----------------------
 |  Global variables
 -----------------------*/
WORD_ALIGNED_ATTR unsigned char TCP_tx_buf[TCP_BUFFER_BYTE_SIZE] = "";
struct spi_dma_buffer_t spi_buffer_circular_list[SPI_RX_BUFFER_COUNT];

/*----------------------
 |  Wifi handler
 -----------------------*/
static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                                    int32_t event_id, void* event_data){
    if (event_id == WIFI_EVENT_AP_STACONNECTED) {
        wifi_event_ap_staconnected_t* event = (wifi_event_ap_staconnected_t*) event_data;
        ESP_LOGI(TAG_AP, "station "MACSTR" join, AID=%d",
                 MAC2STR(event->mac), event->aid);
    } else if (event_id == WIFI_EVENT_AP_STADISCONNECTED) {
        wifi_event_ap_stadisconnected_t* event = (wifi_event_ap_stadisconnected_t*) event_data;
        ESP_LOGI(TAG_AP, "station "MACSTR" leave, AID=%d",
                 MAC2STR(event->mac), event->aid);
    }
}

/*----------------------
 |  Init: Wifi Acces Point
 -----------------------*/
void wifi_init_softap(void)
{
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));

    wifi_config_t wifi_config = {
        .ap = {
            .ssid = ESP_WIFI_SSID,
            .ssid_len = strlen(ESP_WIFI_SSID),
            .channel = ESP_WIFI_CHANNEL,
            .password = ESP_WIFI_PASS,
            .max_connection = ESP_WIFI_MAX_STA_CON,
            .authmode = WIFI_AUTH_WPA_WPA2_PSK,
            .pmf_cfg = {
                    .required = false,
            },
        },
    };
    if (strlen(ESP_WIFI_PASS) == 0) {
        wifi_config.ap.authmode = WIFI_AUTH_OPEN;
    }

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG_AP, "wifi_init_softap finished. SSID:%s password:%s channel:%d",
             ESP_WIFI_SSID, ESP_WIFI_PASS, ESP_WIFI_CHANNEL);
}

/*----------------------
 |  Init: SPI
 -----------------------*/
//Called after a transaction is queued and ready for pickup by master. We use this to set the handshake line high.
void my_post_setup_cb(spi_slave_transaction_t *trans) {
    gpio_set_level(GPIO_HANDSHAKE, 1);
}

//Called after transaction is sent/received. We use this to set the handshake line low.
void my_post_trans_cb(spi_slave_transaction_t *trans) {
    gpio_set_level(GPIO_HANDSHAKE, 0);
}

/***************************************************************************
 * Initialize SPI
 *
 * SPI initialized to use DMA. 
 * 
****************************************************************************/
static void init_SPI(){
    esp_err_t ret;

    // Configuration for the SPI bus
    spi_bus_config_t buscfg = {
        .mosi_io_num   = GPIO_MOSI,
        .miso_io_num   = GPIO_MISO,
        .sclk_io_num   = GPIO_SCLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1
    };

    //Configuration for the SPI slave interface
    spi_slave_interface_config_t slvcfg = {
        .mode          = 0,
        .spics_io_num  = GPIO_CS,
        .queue_size    = 3,
        .flags         = 0,
        .post_setup_cb = my_post_setup_cb,
        .post_trans_cb = my_post_trans_cb
    };

    // GPIO config for the handshake line.
    gpio_config_t io_conf = {
        .intr_type    = GPIO_INTR_DISABLE,
        .mode         = GPIO_MODE_OUTPUT,
        .pin_bit_mask = (1ull<<GPIO_HANDSHAKE)
    };

    // Configure handshake line as output
    gpio_config(&io_conf);
    // Enable pull-ups on SPI lines so we don't detect rogue pulses when no master is connected.
    gpio_set_pull_mode(GPIO_MOSI, GPIO_PULLUP_ONLY);
    gpio_set_pull_mode(GPIO_SCLK, GPIO_PULLUP_ONLY);
    gpio_set_pull_mode(GPIO_CS, GPIO_PULLUP_ONLY);

    // Initialize SPI slave interface
    ret=spi_slave_initialize(RCV_HOST, &buscfg, &slvcfg, SPI_DMA_CH_AUTO);
    assert(ret == ESP_OK);
}

/***************************************************************************
 * Task : SPI poll
 *
 * Poll data from FPGA in SPI to get spike information
 *
 * SPI frame structure:
 * LSB                           MSB
 * | tstamp  | spikes N0 to NMAX |
 * | 32 bits | NMAX bits         |
 *
 * Spike activity of a neuron is coded on one bit:
 *  * 1 : spike triggered
 *  * 0 : none
 * 
 * Data is interpreted as bytes so as one variable contains 8 neurons:
 *     LSBit                MSBit
 * i.e |N0|N1|N2|N3|N4|N5|N6|N7|
 * 
 * Data are stored in a circurlar list of buffer sent to a queue.
****************************************************************************/
static void spi_poll_task(void *pvParameters){
    spi_slave_transaction_t t;
    unsigned int buffer_id = 0;
    
    init_SPI();

    while(1) {
        // Poll data from SPI sourced by FPGA
        t.length    = SPI_FRAME_BIT_SIZE;
        t.tx_buffer = NULL;
        t.rx_buffer = spi_buffer_circular_list[buffer_id].buf;
        spi_slave_transmit(RCV_HOST, &t, portMAX_DELAY);

        // Push data to the queue
        #ifdef SPI_POLL_LOGS
            ESP_LOGI(TAG_POLL_SPI, "Send data\n");
        #endif
        xQueueSend(queue_spikes, spi_buffer_circular_list[buffer_id].buf, (TickType_t) 0);

        // Switch to next buffer
        buffer_id += 1;
		buffer_id %= SPI_RX_BUFFER_COUNT;
    }

    vTaskDelete(NULL);
}

/***************************************************************************
 * Task : TCP client
 *
 * Receive spikes from SPI poll task via queue.
 * Concatenate buffers.
 * Send data using TCP.
 * 
****************************************************************************/
static void tcp_client_task(void *pvParameters){
    esp_err_t ret;

    const char host_ip[] = TCP_SERVER_IP;
    int addr_family = 0;
    int ip_protocol = 0;
    int sock;

    int err;
    int nb_connect_try = 0;

    while (1) {

        do {
            // Configure socket
            struct sockaddr_in dest_addr;
            dest_addr.sin_addr.s_addr = inet_addr(host_ip);
            dest_addr.sin_family = AF_INET;
            dest_addr.sin_port = htons(TCP_SERVER_PORT);
            addr_family = AF_INET;
            ip_protocol = IPPROTO_IP;

            // Create socket
            sock = socket(addr_family, SOCK_STREAM, ip_protocol);
            if (sock < 0) {
                ESP_LOGE(TAG_TCP_CLIENT, "Unable to create socket: errno %d", errno);
                break;
            }
            ESP_LOGI(TAG_TCP_CLIENT, "Socket created, connecting to %s:%d", host_ip, TCP_SERVER_PORT);

            // Try to connect socket to server
            err = connect(sock, (struct sockaddr *)&dest_addr, sizeof(struct sockaddr_in6));
            if (err != 0) {
                nb_connect_try++;
                ESP_LOGE(TAG_TCP_CLIENT, "Socket unable to connect: errno %d (try: %d)", errno, nb_connect_try);
                usleep(500000); // 500 ms
                shutdown(sock, 0);
                close(sock);
            }
        } while (err != 0 && nb_connect_try < TCP_CLIENT_MAX_CONNECT_TRY );

        // Return to main if all try done
        if (nb_connect_try >= TCP_CLIENT_MAX_CONNECT_TRY )
            break;

        ESP_LOGI(TAG_TCP_CLIENT, "Successfully connected\n------------------------------\n");


        /*----------------------
        |  Get and send SPI data
        -----------------------*/
        // unsigned char ts[4] = "";
        // unsigned int* ptr_ts = &ts;
        // unsigned int ts_track = 0; 
        // unsigned int err_cnt = 0;
        while(1){
            // Receive frame buffer from spi task
            for (unsigned int i = 0; i < NB_FRAME_PER_BUFFER; i++){
                xQueueReceive(queue_spikes, TCP_tx_buf+i*SPI_FRAME_BYTE_SIZE, portMAX_DELAY);
            }

            // // Debug tstamp
            // for (unsigned int z = 0; z < NB_FRAME_PER_BUFFER; z++){
            //     ts[0] = TCP_tx_buf[z*SPI_FRAME_BYTE_SIZE+0];
            //     ts[1] = TCP_tx_buf[z*SPI_FRAME_BYTE_SIZE+1];
            //     ts[2] = TCP_tx_buf[z*SPI_FRAME_BYTE_SIZE+2];
            //     ts[3] = TCP_tx_buf[z*SPI_FRAME_BYTE_SIZE+3];
            //     if (*ptr_ts != ts_track){
            //         err_cnt++;
            //     }
            //     ts_track++;
            // }
            // if (err_cnt>0){
            //     printf("err: %u\n", err_cnt);
            // }
            // else{
            //     printf("ok\n");
            // }
                        
            int bytes_written = send(sock, TCP_tx_buf, sizeof(TCP_tx_buf), 0);
            if (bytes_written < 0) {
                ESP_LOGE(TAG_TCP_CLIENT, "Error occurred during sending: errno %d", errno);
                break;
            }
        }

        // Check if socket alive
        if (sock != -1) {
            ESP_LOGE(TAG_TCP_CLIENT, "Shutting down socket and restarting...");
            shutdown(sock, 0);
            close(sock);
        }
    }

    vTaskDelete(NULL);
}

void app_main(void)
{
    // Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Create queue
    queue_spikes = xQueueCreate(QUEUE_SPIKES_LENGTH, sizeof(struct spi_dma_buffer_t));

    // Initialize Wifi in access point mode
    ESP_LOGI(TAG_AP, "ESP_WIFI_MODE_AP");
    wifi_init_softap();

    // Start SPI poll task
    ESP_LOGI(TAG_TCP_CLIENT, "Start SPI poll task");
    xTaskCreatePinnedToCore(spi_poll_task, "spi_poll", 4096, NULL, SPI_POLL_TASK_PRIO, NULL, 0); // on core 0

    // Start TCP client task
    ESP_LOGI(TAG_TCP_CLIENT, "Start TCP client task");
    xTaskCreatePinnedToCore(tcp_client_task, "tcp_client", 4096, NULL, TCP_CLIENT_TASK_PRIO, NULL, 1); // on core 1
}