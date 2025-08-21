# Library-Management
Overview
A comprehensive Odoo module for managing library operations including book cataloging, author management, and rental tracking system.

Features

Core Models

Books Management: Complete book catalog with ISBN, publication details, and cover images
Authors Management: Author profiles with biographical information
Rental System: Track book rentals, returns, and status

Security & Access Control

Dual User Groups:
Library Users: Can only access records they created
Library Managers: Full administrative access to all records
Record-level Security: Custom security rules based on responsible users
Menu Restrictions: Role-based menu visibility


Smart Features
Real-time Availability: Computed field showing book availability status
Rental Constraints: Prevents double-booking of books
Smart Buttons: Quick access to active rentals from book forms
Visual Indicators: Color-coded availability status

Workflow Management
Rental States: Draft → Rented → Returned/Lost
Automated Date Tracking: Automatic rental and return date handling
Status Management: Comprehensive state management for rentals

Installation
Place the module in your Odoo addons directory
Install the module through Odoo Apps menu
Configure user groups and permissions as needed

Configuration

User Groups Setup
Assign users to appropriate groups:
Library User for regular staff
Library Manager for administrative staff

Initial Setup

Add authors to the system
Create book records with author associations
Configure rental policies as needed

Usage
For Library Users
View Books: Access the books menu to see available titles

Manage Rentals:
Create rental records for customers
Track rental status and due dates
Process returns and mark lost books

Author Management: Maintain author information
For Library Managers
Full Access: Complete CRUD operations on all records

System Oversight: Monitor all library activities
User Management: Assign and manage user permissions

Technical Details
Models
library.book: Book catalog with availability tracking
library.author: Author information management
library.rental: Rental transaction records

Dependencies
base
mail

Security
Custom security groups and record rules
User-specific data access
Manager-level oversight capabilities

Business Logic
Availability Rules
A book is considered available if:
No active rentals exist with state 'rented'
No lost book records exist without return dates

Rental Constraints
Prevents renting books that are already rented or lost
Ensures data consistency between rental states and dates
Validates book availability before confirming rentals

Version Information
Odoo Version: 18.0
Module Version: 18.0.1.0.0
License: LGPL-3


Changelog
Version 18.0.1.0.0
Initial release for Odoo 18

Complete library management system
Advanced security features
Comprehensive rental tracking

********************************************** THERE ARE SOME ADDITIONAL FEATURES WE COULD ADD*******************************************

* WE COULD CREATE PORTAL PAGE FOR BORROWERS TO TRACH THEIR RENTAL DETAILS
* EACH BORROWER WILL BE ABLE TO SEE HOS OWN RENTALS ONLY 
* WE COULD MAKE DEALINE FOT THE DURATION OF RENTAL (ONE MONTH FOR EXAMPLE) THE DAY WHICH HE WILL RETURN THE BOOK
* WHEN THE BORROWER DELIVERS THE BOOK HE DELIVERS A MESSAGE ON WHATSAPP CONFIRMS THE RENTAL DATE OF THE BOOK
* AND ONE DAY BEFORE THE DEADLINE HE RECEIVS AN OTHER MESSAGE REMINDS HIM WITH THE RETURN DATE
* WHATSAPP MESSAGES ARE AUTOMATED JUST A CLICK OF A BUTTON
* WE COULD CREATE KANBAN AND CALENDAR VIEWS 
* WE COULD CREATE A DASHBOARD (JS) TO TRACK THE BOOKS 
* DASHBOARD WILL CONTAIN ALL BOOKS AND BORROWERS AND DEADLINES FILTERING BOOKS BASED ON AVAILABILITY ALL IN ONE SCREEN
