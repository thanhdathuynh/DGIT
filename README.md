# DGIdb Gene-Drug Interaction Tool

A comprehensive Flask web application that enables users to search for drug-gene interactions using the [DGIdb GraphQL API](https://dgidb.org/api/graphql), with integrated AI assistance and database caching capabilities.

## Overview

This tool provides an interactive interface for exploring gene-drug interactions, with a specific focus on **Major Depressive Disorder (MDD)**. While the DGIdb contains interactions for a wide range of conditions, this application is specifically designed to help researchers and healthcare professionals identify therapeutic targets and insights into gene-related drug interactions relevant to MDD treatment and research.

## Key Features

- **Advanced Search**: Query drug-gene interactions using the DGIdb GraphQL API
- **AI Assistant**: Integrated Google Generative AI chatbot for instant answers about gene-drug interactions
- **Database Caching**: MySQL database integration for caching search results and improving performance
- **MDD-Specific Data**: Pre-configured lists of MDD-relevant genes, proteins, and drugs
- **Modern UI**: Responsive web interface with dedicated pages for search, database views, about, and contact

### MDD-Relevant Entities

**Genes**: SLC6A4, BDNF, HTR2A, TPH2, GNB3, MTHFR, DRD2, CELF4, LAMB2, FKBP5

**Proteins**: BDNF, IL-6, CRP, TNF‑α, ITIH4, CD155, Lipocalin-2, HGF, LIGHT, C1QC

**Drugs**: Fluoxetine, Sertraline, Venlafaxine, Levomilnacipran, Citalopram, Escitalopram, Milnacipran, Trazodone, Mirtazapine, Vortioxetine

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL database server
- pip package manager

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/thanhdathuynh/DGIT.git
   cd DGIT
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the root directory with your database and API credentials:

   ```env
   MYSQL_HOST=your_mysql_host
   MYSQL_USER=your_mysql_user
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=your_database_name
   GOOGLE_API_KEY=your_google_api_key
   ENTREZ_EMAIL=your_email
   ENTREZ_API_KEY=your_entrez_api_key
   ```

4. **Run the application**

   ```bash
   python3 app.py
   ```

5. **Access the application**

   Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
DGIT/
├── app.py              # Main Flask application with routes
├── db_conn.py          # Database connection and caching logic
├── ai_helper.py        # Google Generative AI integration
├── gene_mapping.py     # Gene mapping utilities
├── requirements.txt    # Python dependencies
├── static/             # CSS stylesheets
│   ├── about.css
│   ├── ai-chatbot.css
│   ├── contact.css
│   ├── db.css
│   ├── index.css
│   ├── nav.css
│   ├── search.css
│   └── style.css
└── templates/          # HTML templates
    ├── about.html
    ├── contact.html
    ├── db.html
    ├── index.html
    ├── nav.html
    └── search.html
```

## Usage

### Search for Interactions

1. Navigate to the **Search** page
2. Enter a gene name, drug name, or interaction term
3. View detailed results including interaction types, sources, and PMIDs
4. Results are automatically cached for faster subsequent queries

### AI Chatbot

1. Use the AI chatbot interface to ask questions about gene-drug interactions
2. Get instant AI-powered responses about MDD-related genes, drugs, and their interactions
3. Powered by Google's Generative AI (Gemini)

### Database View

Access the **Database** page to view previously cached search results and interaction data stored in your MySQL database.

## Technologies Used

- **Backend**: Flask 3.1.1, Python 3.x
- **Database**: MySQL with Flask-MySQLdb
- **AI Integration**: Google Generative AI (Gemini)
- **API**: DGIdb GraphQL API
- **Frontend**: HTML5, CSS3, Jinja2 templates

## API Routes

- `/` - Home page
- `/search` - Search for gene-drug interactions
- `/db` - View cached database results
- `/about` - About the project
- `/contact` - Contact form
- `/ask` - AI chatbot endpoint (POST)

## References

The relevance of gene-drug interactions in MDD is supported by the following literature:

- **Overview of the Genetics of Major Depression Disorder**: Discusses genetic markers associated with antidepressant efficacy. [Read more](https://pmc.ncbi.nlm.nih.gov/articles/PMC3077049/)

- **Molecular pathways of major depressive disorder converge on the synapse**: Reviews evidence linking drug efficacy and gene variations in MDD treatment. [Read more](https://pmc.ncbi.nlm.nih.gov/articles/PMC9540059/)

- **Major Depressive Disorder (StatPearls)**: Overview of MDD diagnosis, treatment, and pathophysiology. [Read more](https://www.ncbi.nlm.nih.gov/books/NBK559078/)

- **DGIdb**: The Drug Gene Interaction Database. [Visit DGIdb](https://dgidb.org/)

**Note**: This tool is intended for research and educational purposes. Always consult with healthcare professionals for medical decisions.
