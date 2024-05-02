/*
*! @title      Axi lite object
*! @file       AxiLite.cpp
*! @author     Romain Beaubois
*! @date       10 Aug 2022
*! @copyright
*! SPDX-FileCopyrightText: © 2021 Romain Beaubois <refbeaubois@yahoo.com>
*! SPDX-License-Identifier: GPL-3.0-or-later
*!
*! @brief
*! Axi lite object
*! * Store pointer to base address to handle axi as C array
*! * Store numbers of read and write registers (PS pov, so FPGA read is PS write)
*! * Read/write functions
*! 
*! @details
*! > **15 Sep 2021** : file creation (RB)
*! > **10 Aug 2022** : adapt axilite to zubuntu and userspace access (RB)
*! > **21 Dec 2022** : add constructor with range setup (RB)
*/

#include "AxiLite.h"

/***************************************************************************
 * Initialize AxiLite object
 * 
 * @param base_addr Base address of AXI object in platform
 * @param nb_regs_write Number of write register (from PS pov, fpga pov is read register)
 * @param nb_regs_read Number of read register (from PS pov, fpga pov is read register)
 * @return None
****************************************************************************/
AxiLite::AxiLite(uint64_t base_addr, uint64_t range, uint16_t nb_regs_write, uint16_t nb_regs_read){
    int r;
    int fd;

    // Set AxiLite propertoes
    _nb_regs_write  = nb_regs_write;
    _nb_regs_read   = nb_regs_read;
    _nb_regs        = nb_regs_read + nb_regs_write;

    // Get file descriptor for /dev/mem
    fd = open("/dev/mem", O_RDWR | O_SYNC);
    r = (fd == -1) ? EXIT_FAILURE : EXIT_SUCCESS;
    statusPrint(r, "Open file /dev/mem");

    if(fd != -1){
        // Map physical address into user space by getting a virtual address
        _axi_regs_u32_vptr = (uint32_t *)mmap(NULL, range, PROT_READ|PROT_WRITE, MAP_SHARED, fd, base_addr);
        r = (_axi_regs_u32_vptr == NULL) ? EXIT_FAILURE : EXIT_SUCCESS;
        statusPrint(r, "Map pointer to virtual address of axi lite");
    
        // Close file descriptor of /dev/mem
        close(fd);
        statusPrint(EXIT_SUCCESS, "Close file /dev/mem");
    }
}

/***************************************************************************
 * Write in AXI lite register
 * 
 * @param wdata Data to write
 * @param regw Axi register index to write in
 * @return None
****************************************************************************/
int AxiLite::write(uint32_t wdata, uint16_t regw){
    _axi_regs_u32_vptr[regw] = wdata;
    return EXIT_SUCCESS;
}

/***************************************************************************
 * Write in AXI lite register from float
 * 
 * @param wdata Data to write as float
 * @param regw Axi register index to write in
 * @return None
****************************************************************************/
int AxiLite::write(float wdata, uint16_t regw, uint8_t fp_int, uint8_t fp_dec){
    _axi_regs_u32_vptr[regw] = float2sfi(wdata, fp_int, fp_dec);
    return EXIT_SUCCESS;
}

/***************************************************************************
 * Read from AXI lite register
 * 
 * @param regr Axi register index to read from
 * @return Value of Axi register at regr index
****************************************************************************/
uint32_t AxiLite::read(uint16_t regr){
    return _axi_regs_u32_vptr[regr];
}

/***************************************************************************
 * Read from AXI lite register as a float
 * 
 * @param regr Axi register index to read from
 * @param fp_int Fixed point integer part coding
 * @param fp_dec Fixed point decimal part coding
 * @return Value of Axi register at regr index as float
****************************************************************************/
float AxiLite::read(uint16_t regr, uint8_t fp_int, uint8_t fp_dec){
    return sfi2float(_axi_regs_u32_vptr[regr], fp_int, fp_dec);
}

/***************************************************************************
 * Read/Write test on AXI registers
 * 
 * @return XStatus (Success if test passed, else failure)
****************************************************************************/
int AxiLite::test_RW(){
    // Display actual test running
    infoPrint(0, "Write/read on AXI registers");
    
    // Status variable
    int status;

    // Assure that r_data differs from w_data (prevent the case where w_data = 0 and at init r_data)
    uint32_t wdata = 0;
    uint32_t rdata = wdata + 10;

    // Write in registers
    for (uint32_t waddr = 0; waddr < _nb_regs_write; waddr++)
    {
        status = this->write(wdata+waddr, waddr);
        if (status == EXIT_FAILURE)
            statusPrint(status, "Write in registers");
    }    
    statusPrint(EXIT_SUCCESS, "Write in registers");
    
    // Read registers
    status = EXIT_SUCCESS;
    for (uint32_t raddr = 0; raddr < _nb_regs_write; raddr++)
    {
        rdata = this->read(raddr);
        if (rdata != (wdata+raddr)){
            status = EXIT_FAILURE;
        }
    }
    statusPrint(status, "Read from registers");

    return status;
}
