
## ****Asset Management (Odoo 18)****


Assign, Track, and Manage Company Assets — The Smart Way 💻📦🔧
****
This module helps businesses manage their physical assets (like laptops, desktops, and appliances) by tracking issuance, returns, and current ownership — whether assigned to employees, departments, or external clients.

Designed for simplicity, built for power. Multi-company support included.

---

🚀 Core Features
----------------

✅ Asset Issuance:
   - Assign assets to **Employees**, **Departments**, or **Clients (Customers)**
   - duplicate prevention
   - Track status: `validated`, `approved`. `issued`, `rejected` etc

✅ Asset Return:
   - Returns handled per user, department, or client
   - Automatically populates assets currently assigned to the requester
   - duplicate prevention
   - Track status: `validated`, `approved`. `issued`, `rejected` etc

✅ Asset Location Tracking:
   - Configure and manage **asset locations**
   - View assets currently in a location via smart buttons

✅ Categorization:
   - Custom asset categories (e.g., Laptop, Monitor, Appliance)

✅ Multi-Company Ready:
   - Records are isolated per company
   - Each company can have its own assets, serials, and users

✅ Unique Serial Per Company:
   - Ensure **no duplicate serials per company**
   - Serial field is optional per asset category

✅ Smart Chatter Logs:
   - All major asset actions (issuance, return, location changes) are logged

✅ Clean and Secure Role-Based Access:
   - **Asset User** – can request issuance/return
   - **Asset Officer** – can validate requests
   - **Asset Manager** – can approve, reject, and manage all

✅ Field Integration with Odoo HR:
   - `asset_location_id` added to Employees, Departments, and Clients

---

🧩 Extensible with Premium Add-ons
----------------------------------

This core module is the foundation of a complete asset suite. Upcoming/premium modules:

- `ll_asset_history` – Issuance and return history views
- `ll_asset_report` – Export reports (Excel, PDF)
- `ll_asset_replacement` – Replacement process workflow
- `ll_asset_maintenance` – Maintenance logs and status tracking
- `ll_asset_accounting` – Link with Odoo’s depreciation
- `ll_asset_bundle` – Manage asset kits (like laptop sets with charger & bag)
- `ll_asset_purchase_request` – Purchase request integration

> 🎯 Modular design: Only install what you need.

---

📸 Screenshots
--------------

---

🙋 Frequently Asked Questions (FAQ)
-----------------------------------

**Q: Is this compatible with Odoo Enterprise?**  
A: This is tested on **Odoo 18 Community Edition**. It may work on Enterprise but is not guaranteed or officially supported.

**Q: Can I issue and return assets to departments and external clients?**  
A: Yes, you can assign and return assets to employees, departments, or clients (res.partner).

**Q: Does this handle asset depreciation?**  
A: No, but the optional `ll_asset_accounting` module will handle that.

**Q: What if two companies have assets with the same serial?**  
A: That’s fine! The app ensures **serials are unique *per company***, not globally.

---

🛠 Support & Contact
--------------------

📧 Email: lslanzaderas@gmail.com  
🌐 Website: https://lawrencelanzaderas-portfolio.netlify.app 
📦 License: OEEL-1  
