# 🛒 IDENHQ Product Scraper

This project automates the process of logging into [hiring.idenhq.com](https://hiring.idenhq.com/), navigating through the dashboard to the **Full Catalog**, and scraping detailed product information using **Playwright** (Python).

The extracted data is exported to a clean `products.json` file.

---

## 📦 Features

- Secure Login and Session Handling
- Dashboard Navigation
- Full Product Catalog Scraping
- Product Details Extraction:
  - Title
  - ID
  - Category
  - Rating
  - Cost
  - Details
  - Last Updated
- JSON Export of all products
- Error Handling & Debug Logs

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/harshgunjal/idenhq-Project.git
cd idenhq-Project

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

---

## ⚙️ Requirements

- Python 3.8+
- Playwright

Install Playwright browsers after installing:

```bash
playwright install
```

---

## 🔐 Environment Variables

Create a `.env` file or directly set environment variables:

| Variable        | Description                  |
|-----------------|-------------------------------|
| `IDEN_EMAIL`    | Your login email for IDENHQ   |
| `IDEN_PASSWORD` | Your password for IDENHQ      |

If environment variables are **not set**, the script uses fallback default credentials.

---

## 🛠️ Usage

```bash
python main.py
```

The script will:
- Log in to IDENHQ
- Launch the challenge
- Navigate to Full Catalog
- Scrape all product cards
- Export the data to `products.json`

---

## 📄 Output

The final `products.json` will look like:

```json
[
    {
        "title": "Eco-friendly Books System",
        "id_and_category": {
            "id": "1234",
            "category": "Books"
        },
        "rating": "4.8",
        "cost": "$25",
        "details": "Hardcover",
        "last_updated": "2 days ago"
    },
    ...
]
```

---

## 🐞 Troubleshooting

- **Timeout Errors**: Check your internet connection or increase timeout values.
- **Selectors Not Found**: The website structure might have changed — update selectors inside `extract_product_data()` accordingly.
- **Session Errors**: Delete `session.json` and rerun.
