Created 18-JUL-2019

Updated 08-FEB-2022

Copyright (c) 2023 Oracle and/or its affiliates. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions rem of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.

NAME
  README.txt - ReadMe text file for CO schema

DESCRIPTION
  Customer Orders (CO) is a sample schema resembling a generic
  customer orders management schema.
  The Customer Orders (CO) schema records the details of transactions made by
  a retail application.

  The CO schema highlights features such as JSON support.

  The company sells a variety of products, which are maintained in the products
  table. Each product has a unique identification number, name, price, details
  stored in a JSON object and product image details.

  The orders placed by the customer are tracked in the orders table using the
  order identification number, date and time when the order was placed,
  customer details, order status and the store information.

  The details of the products in a particular order are also tracked in the
  order_items table using the order identification number. Details of the
  products, price at the time of purchase, quantity and shipment are recorded.

  The information of a customer placing an order is tracked in the customers
  table. Each customer has an identification number, name, and email address
  that is used for communication of the orders.

  The customers can purchase the products in stores or online through the
  company's website. The information for all of the stores and their
  corresponding physical and virtual addresses is tracked in the stores
  table. The store information is also recorded in the order details.

  The shipment details of the orders placed such as the delivery address,
  customer details, store information and the shipment status are stored
  in the shipments table.

  An inventory table stores the details of each product such as the quantity
  available at each store.

SCHEMA VERSION
  21

RELEASE DATE
  08-FEB-2022

SUPPORTED with DB VERSIONS
  19c and higher

MAJOR CHANGES IN THIS RELEASE
  1. simplified installation
  2. all date data is updated

SCHEMA DEPENDENCIES AND REQUIREMENTS
 Required access to cp_install.sql, co_create.sql, co_populate.sql

INSTALL INSTRUCTIONS
  1. Run as privileged user with rights to create another user 
     (SYSTEM, ADMIN, etc.)
  2. Run the co_install.sql script to create the CO (Customer Orders) schema
  3. You are prompted for:
     a. password - enter an Oracle Database compliant password
     b. tablespace - if you do not enter a tablespace, the default 
        database tablespace is used
  Note: If the CO schema already exists, it is removed/dropped and 
        a fresh CO schema is installed

UNINSTALL INSTRUCTIONS
  1. Run as privileged user with rights to create another user 
     (SYSTEM, ADMIN, etc.)
  2. Run the co_uninstall.sql script to remove the CO (Customer Orders) schema

NOTES
  Scripts need to be run as a privileged user with rights to create
  another user (SYSTEM, ADMIN, etc.)

--------------------------------------------------------------------------
