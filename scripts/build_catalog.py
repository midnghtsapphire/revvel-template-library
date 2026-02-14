#!/usr/bin/env python3
"""
Build the comprehensive template catalog database.
Merges research data + adds hundreds of additional templates from known sources.
"""
import json
import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = "/home/ubuntu/revvel-template-library/catalog/templates.db"
CATALOG_JSON = "/home/ubuntu/revvel-template-library/catalog/templates.json"

def parse_json_file(filepath):
    """Parse JSON files that may contain multiple JSON arrays."""
    entries = []
    with open(filepath) as f:
        content = f.read()
    
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(content):
        stripped = content[idx:].lstrip()
        if not stripped:
            break
        try:
            obj, end = decoder.raw_decode(stripped)
            if isinstance(obj, list):
                entries.extend(obj)
            elif isinstance(obj, dict):
                entries.append(obj)
            idx += len(content) - len(stripped) + end
        except json.JSONDecodeError:
            idx += 1
    return entries

def create_database():
    """Create the SQLite database schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("DROP TABLE IF EXISTS templates")
    c.execute("DROP TABLE IF EXISTS categories")
    c.execute("DROP TABLE IF EXISTS sources")
    
    c.execute("""
        CREATE TABLE categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            parent_id TEXT,
            description TEXT,
            icon TEXT,
            FOREIGN KEY (parent_id) REFERENCES categories(id)
        )
    """)
    
    c.execute("""
        CREATE TABLE sources (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT,
            description TEXT,
            is_free INTEGER DEFAULT 1
        )
    """)
    
    c.execute("""
        CREATE TABLE templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            source TEXT,
            source_url TEXT,
            download_url TEXT,
            format TEXT DEFAULT 'MD',
            description TEXT,
            is_free INTEGER DEFAULT 1,
            tags TEXT,
            file_path TEXT,
            has_file INTEGER DEFAULT 0,
            created_at TEXT,
            popularity INTEGER DEFAULT 0,
            author TEXT,
            seo_keywords TEXT
        )
    """)
    
    c.execute("CREATE INDEX idx_templates_category ON templates(category)")
    c.execute("CREATE INDEX idx_templates_subcategory ON templates(subcategory)")
    c.execute("CREATE INDEX idx_templates_tags ON templates(tags)")
    c.execute("CREATE INDEX idx_templates_format ON templates(format)")
    c.execute("CREATE INDEX idx_templates_is_free ON templates(is_free)")
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS templates_fts USING fts5(name, description, tags, category, subcategory)")
    
    conn.commit()
    return conn

def insert_categories(conn):
    """Insert category hierarchy."""
    categories = [
        # Top-level
        ("legal", "Legal", None, "Legal documents, contracts, and court filings", "⚖️"),
        ("academic", "Academic & Research", None, "Academic papers, research templates, and scholarly documents", "🎓"),
        ("business", "Business", None, "Business plans, financial documents, and corporate templates", "💼"),
        ("government", "Government & Regulatory", None, "Government forms, regulatory filings, and compliance documents", "🏛️"),
        ("foss", "FOSS & Developer", None, "Open source project templates and developer documentation", "💻"),
        ("personal", "Personal & Finance", None, "Personal documents, financial planning, and life events", "👤"),
        
        # Legal subcategories
        ("legal-contracts", "Contracts & Agreements", "legal", "Business and personal contracts", None),
        ("legal-estate", "Wills & Estate Planning", "legal", "Estate planning and inheritance documents", None),
        ("legal-real-estate", "Real Estate", "legal", "Property and real estate legal documents", None),
        ("legal-family", "Family Law", "legal", "Divorce, custody, and family legal documents", None),
        ("legal-business", "Business Formation", "legal", "LLC, corporation, and partnership documents", None),
        ("legal-court", "Court Filings", "legal", "Legal briefs, motions, and court documents", None),
        ("legal-ip", "Intellectual Property", "legal", "Patents, trademarks, and copyright documents", None),
        ("legal-employment", "Employment Law", "legal", "Employment contracts and workplace documents", None),
        ("legal-trusts", "Trusts", "legal", "Trust formation and management documents", None),
        ("legal-compliance", "Compliance", "legal", "Regulatory compliance and policy documents", None),
        
        # Academic subcategories
        ("academic-papers", "Research Papers", "academic", "Research paper templates in various citation styles", None),
        ("academic-thesis", "Thesis & Dissertation", "academic", "Graduate thesis and doctoral dissertation templates", None),
        ("academic-grants", "Grant Proposals", "academic", "Research funding and grant application templates", None),
        ("academic-posters", "Academic Posters", "academic", "Conference poster and presentation templates", None),
        ("academic-cv", "Academic CV", "academic", "Curriculum vitae for academic professionals", None),
        ("academic-whitepapers", "White Papers", "academic", "Technical and policy white paper templates", None),
        ("academic-latex", "LaTeX Templates", "academic", "LaTeX document classes and templates", None),
        
        # Business subcategories
        ("business-plans", "Business Plans", "business", "Business plan and strategy documents", None),
        ("business-finance", "Financial Documents", "business", "Financial statements, projections, and budgets", None),
        ("business-marketing", "Marketing", "business", "Marketing plans, campaigns, and analysis", None),
        ("business-hr", "Human Resources", "business", "HR forms, policies, and employee documents", None),
        ("business-operations", "Operations", "business", "Project management and operational documents", None),
        ("business-sales", "Sales & Proposals", "business", "Sales proposals, quotes, and pitch decks", None),
        ("business-invoicing", "Invoicing & Billing", "business", "Invoices, receipts, and billing templates", None),
        
        # Government subcategories
        ("gov-tax", "Tax & IRS", "government", "Tax forms and IRS-related documents", None),
        ("gov-business", "Business Registration", "government", "Government business registration and licensing", None),
        ("gov-ip", "Patents & Trademarks", "government", "USPTO filings and IP registration", None),
        ("gov-foia", "FOIA & Public Records", "government", "Freedom of Information Act and public records requests", None),
        ("gov-contracts", "Government Contracts", "government", "Federal and state contracting documents", None),
        ("gov-grants", "Government Grants", "government", "Federal and state grant applications", None),
        ("gov-compliance", "Regulatory Compliance", "government", "Environmental, safety, and regulatory forms", None),
        
        # FOSS subcategories
        ("foss-github", "GitHub Templates", "foss", "Repository templates and GitHub-specific files", None),
        ("foss-docs", "Documentation", "foss", "Technical documentation and API docs templates", None),
        ("foss-devops", "DevOps & Infrastructure", "foss", "CI/CD, deployment, and infrastructure templates", None),
        ("foss-project", "Project Management", "foss", "Open source project management templates", None),
        ("foss-security", "Security", "foss", "Security policies, incident response, and audit templates", None),
    ]
    
    c = conn.cursor()
    for cat in categories:
        c.execute("INSERT INTO categories VALUES (?, ?, ?, ?, ?)", cat)
    conn.commit()

def insert_sources(conn):
    """Insert known template sources."""
    sources = [
        ("rocket-lawyer", "Rocket Lawyer", "https://www.rocketlawyer.com", "Legal document templates and attorney services", 0),
        ("lawdepot", "LawDepot", "https://www.lawdepot.com", "Free legal forms and templates", 1),
        ("eforms", "eForms", "https://eforms.com", "Free legal forms for every state", 1),
        ("us-legal", "US Legal Forms", "https://www.uslegalforms.com", "Legal forms database", 0),
        ("legalzoom", "LegalZoom", "https://www.legalzoom.com", "Legal services and document templates", 0),
        ("nolo", "Nolo", "https://www.nolo.com", "Legal information and forms", 1),
        ("findlaw", "FindLaw", "https://www.findlaw.com", "Legal information and resources", 1),
        ("legal-templates", "LegalTemplates.net", "https://legaltemplates.net", "Free legal document templates", 1),
        ("overleaf", "Overleaf", "https://www.overleaf.com/latex/templates", "LaTeX templates gallery", 1),
        ("ieee", "IEEE", "https://www.ieee.org", "IEEE paper and conference templates", 1),
        ("acm", "ACM", "https://www.acm.org", "ACM publication templates", 1),
        ("score", "SCORE", "https://www.score.org", "Free business mentoring and templates", 1),
        ("sba", "SBA", "https://www.sba.gov", "Small Business Administration resources", 1),
        ("hubspot", "HubSpot", "https://www.hubspot.com", "Marketing and business templates", 1),
        ("irs", "IRS", "https://www.irs.gov", "Internal Revenue Service forms", 1),
        ("uspto", "USPTO", "https://www.uspto.gov", "Patent and trademark office", 1),
        ("github", "GitHub", "https://github.com", "Open source templates and repos", 1),
        ("cncf", "CNCF", "https://www.cncf.io", "Cloud Native Computing Foundation", 1),
        ("scribd", "Scribd", "https://www.scribd.com", "Document sharing platform", 0),
        ("pdfiller", "PDFiller", "https://www.pdffiller.com", "PDF forms and templates", 0),
        ("pandadoc", "PandaDoc", "https://www.pandadoc.com", "Document automation platform", 0),
        ("docusign", "DocuSign", "https://www.docusign.com", "Electronic signature and templates", 0),
        ("smartsheet", "Smartsheet", "https://www.smartsheet.com", "Project management templates", 0),
        ("microsoft", "Microsoft Office", "https://templates.office.com", "Office document templates", 1),
        ("google", "Google Docs", "https://docs.google.com/templates", "Google Workspace templates", 1),
        ("canva", "Canva", "https://www.canva.com", "Design and document templates", 1),
        ("revvel", "Revvel Original", "https://github.com/MIDNGHTSAPPHIRE/revvel-template-library", "Original templates created for this library", 1),
        ("courtlistener", "CourtListener", "https://www.courtlistener.com", "Free legal research and court opinions", 1),
        ("ssrn", "SSRN", "https://www.ssrn.com", "Social Science Research Network", 1),
        ("springer", "Springer", "https://www.springer.com", "Academic publisher templates", 1),
        ("elsevier", "Elsevier", "https://www.elsevier.com", "Academic publisher templates", 1),
    ]
    
    c = conn.cursor()
    for src in sources:
        c.execute("INSERT INTO sources VALUES (?, ?, ?, ?, ?)", src)
    conn.commit()

def generate_comprehensive_templates():
    """Generate a massive comprehensive template catalog."""
    templates = []
    
    def add(name, cat, subcat, source, source_url, fmt, desc, is_free, tags, download_url=""):
        templates.append({
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "category": cat,
            "subcategory": subcat,
            "source": source,
            "source_url": source_url,
            "download_url": download_url,
            "format": fmt,
            "description": desc,
            "is_free": 1 if is_free else 0,
            "tags": tags,
            "file_path": "",
            "has_file": 0,
            "created_at": datetime.now().isoformat(),
            "popularity": 0,
            "author": "Walter-Evans",
            "seo_keywords": tags
        })
    
    # ==========================================
    # LEGAL TEMPLATES - Comprehensive Collection
    # ==========================================
    
    # Contracts & Agreements
    contracts = [
        ("Non-Disclosure Agreement (NDA) - Mutual", "Mutual NDA protecting both parties' confidential information in business dealings."),
        ("Non-Disclosure Agreement (NDA) - One-Way", "One-directional NDA where only one party discloses confidential information."),
        ("Non-Disclosure Agreement (NDA) - Employee", "NDA specifically for employees handling proprietary company information."),
        ("Independent Contractor Agreement", "Agreement defining the relationship between a company and an independent contractor."),
        ("Freelance Services Agreement", "Contract for freelance work including scope, payment terms, and deliverables."),
        ("Consulting Agreement", "Professional consulting services contract with scope of work and compensation terms."),
        ("Master Services Agreement (MSA)", "Umbrella agreement governing the overall relationship between service provider and client."),
        ("Software License Agreement", "License terms for software use, distribution, and modification rights."),
        ("SaaS Subscription Agreement", "Terms for Software-as-a-Service subscription including SLA and data handling."),
        ("Joint Venture Agreement", "Agreement between parties to undertake a specific business project together."),
        ("Non-Compete Agreement", "Restrictive covenant preventing competition after employment or business relationship ends."),
        ("Non-Solicitation Agreement", "Agreement preventing solicitation of clients, customers, or employees."),
        ("Service Level Agreement (SLA)", "Defines expected service levels, metrics, and remedies for service providers."),
        ("Memorandum of Understanding (MOU)", "Preliminary agreement outlining terms before a formal contract is executed."),
        ("Letter of Intent (LOI)", "Formal letter expressing intent to enter into a business transaction."),
        ("Purchase Agreement", "Contract for the sale and purchase of goods or assets."),
        ("Sales Agreement", "Agreement governing the sale of products including warranties and delivery terms."),
        ("Distribution Agreement", "Contract granting rights to distribute products in specified territories."),
        ("Agency Agreement", "Agreement appointing an agent to act on behalf of a principal."),
        ("Commission Agreement", "Contract defining commission-based compensation for sales or referrals."),
        ("Referral Agreement", "Agreement for referral fees and terms between business partners."),
        ("Sponsorship Agreement", "Contract for event or content sponsorship including deliverables and compensation."),
        ("Licensing Agreement", "Agreement granting rights to use intellectual property under specified terms."),
        ("Franchise Agreement", "Contract governing the franchisor-franchisee relationship."),
        ("Loan Agreement - Personal", "Personal loan contract between individuals with repayment terms."),
        ("Loan Agreement - Business", "Business loan agreement with interest rates, collateral, and repayment schedule."),
        ("Promissory Note", "Written promise to pay a specified sum on demand or at a future date."),
        ("Bill of Sale", "Document transferring ownership of personal property from seller to buyer."),
        ("Assignment Agreement", "Contract transferring rights or obligations from one party to another."),
        ("Indemnification Agreement", "Agreement where one party agrees to compensate another for losses or damages."),
        ("Release of Liability / Waiver", "Document releasing a party from liability for potential claims."),
        ("Settlement Agreement", "Agreement resolving a dispute between parties without litigation."),
        ("Mediation Agreement", "Agreement to resolve disputes through mediation rather than litigation."),
        ("Arbitration Agreement", "Contract requiring disputes to be resolved through binding arbitration."),
    ]
    for name, desc in contracts:
        add(name, "Legal", "Contracts & Agreements", "Revvel Original", "", "MD", desc, True,
            "contract, agreement, legal, " + name.lower().replace(" ", ", ").replace("(", "").replace(")", ""))
    
    # Real Estate
    real_estate = [
        ("Residential Lease Agreement", "Standard residential rental agreement for landlords and tenants."),
        ("Commercial Lease Agreement", "Lease agreement for commercial property including business-specific terms."),
        ("Month-to-Month Rental Agreement", "Flexible rental agreement without a fixed term, renewable monthly."),
        ("Sublease Agreement", "Agreement allowing a tenant to sublease their rental to a third party."),
        ("Room Rental Agreement", "Agreement for renting a room within a shared living space."),
        ("Lease Termination Letter", "Formal notice to terminate a lease agreement."),
        ("Eviction Notice - 3 Day", "Three-day notice to pay rent or quit the premises."),
        ("Eviction Notice - 30 Day", "Thirty-day notice to vacate the rental property."),
        ("Eviction Notice - 60 Day", "Sixty-day notice to vacate, typically for month-to-month tenancies."),
        ("Rental Application", "Application form for prospective tenants including background check authorization."),
        ("Property Management Agreement", "Contract between property owner and management company."),
        ("Real Estate Purchase Agreement", "Contract for the sale and purchase of real property."),
        ("Quitclaim Deed", "Deed transferring property interest without warranties of title."),
        ("Warranty Deed", "Deed transferring property with full warranties of clear title."),
        ("Land Contract / Contract for Deed", "Installment sale agreement for real property."),
        ("Lease Option Agreement", "Agreement giving tenant the option to purchase the leased property."),
        ("Property Inspection Checklist", "Move-in/move-out inspection checklist for rental properties."),
        ("Security Deposit Return Letter", "Letter itemizing security deposit deductions and return amount."),
        ("Rent Increase Notice", "Formal notice of rent increase to tenants."),
        ("Lease Renewal Agreement", "Agreement to renew an existing lease with updated terms."),
        ("Tiny Home / Mobile Home Lease Agreement", "Specialized lease for tiny homes and mobile home parks."),
        ("Vacation Rental Agreement", "Short-term rental agreement for vacation properties."),
        ("Commercial Property Purchase Agreement", "Contract for buying/selling commercial real estate."),
    ]
    for name, desc in real_estate:
        add(name, "Legal", "Real Estate", "Revvel Original", "", "MD", desc, True,
            "real estate, property, lease, rental, " + name.lower().split(" - ")[0].replace(" ", ", "))
    
    # Wills & Estate Planning
    estate = [
        ("Last Will and Testament", "Legal document specifying distribution of assets after death."),
        ("Living Will / Advance Directive", "Document expressing healthcare wishes if incapacitated."),
        ("Healthcare Power of Attorney", "Designates someone to make medical decisions on your behalf."),
        ("Financial Power of Attorney", "Authorizes someone to manage financial affairs on your behalf."),
        ("Durable Power of Attorney", "Power of attorney that remains effective if the principal becomes incapacitated."),
        ("Limited Power of Attorney", "Grants specific, limited authority to act on someone's behalf."),
        ("Revocable Living Trust", "Trust that can be modified during the grantor's lifetime."),
        ("Irrevocable Trust", "Trust that cannot be modified once established, providing asset protection."),
        ("Dynasty Trust", "Multi-generational trust designed to pass wealth without estate taxes."),
        ("Family Trust", "Trust established for the benefit of family members."),
        ("Special Needs Trust", "Trust providing for a disabled beneficiary without affecting government benefits."),
        ("Charitable Remainder Trust", "Trust providing income to beneficiary with remainder going to charity."),
        ("Pet Trust", "Trust providing for the care of pets after the owner's death."),
        ("Trust Amendment", "Document modifying terms of an existing trust."),
        ("Trust Certification", "Certificate confirming the existence and terms of a trust."),
        ("Estate Planning Checklist", "Comprehensive checklist for estate planning documents and decisions."),
        ("Beneficiary Designation Form", "Form designating beneficiaries for accounts and policies."),
        ("Letter of Instruction", "Non-legal letter providing guidance to executors and beneficiaries."),
        ("Executor Duties Checklist", "Checklist of responsibilities for estate executors."),
        ("Guardianship Designation", "Document naming a guardian for minor children."),
    ]
    for name, desc in estate:
        add(name, "Legal", "Wills & Estate Planning", "Revvel Original", "", "MD", desc, True,
            "estate planning, trust, will, " + name.lower().replace(" ", ", "))
    
    # Family Law
    family = [
        ("Divorce Agreement / Settlement", "Agreement dividing assets and responsibilities in a divorce."),
        ("Child Custody Agreement", "Agreement establishing custody arrangements for children."),
        ("Child Support Agreement", "Agreement defining child support payment terms."),
        ("Prenuptial Agreement", "Agreement between future spouses regarding asset division."),
        ("Postnuptial Agreement", "Agreement between married spouses regarding asset division."),
        ("Separation Agreement", "Agreement for legally separated spouses."),
        ("Parenting Plan", "Detailed plan for co-parenting including schedules and decision-making."),
        ("Adoption Consent Form", "Legal consent for adoption proceedings."),
        ("Name Change Petition", "Court petition to legally change one's name."),
        ("Guardianship Petition", "Petition to become legal guardian of a minor or incapacitated person."),
        ("Domestic Partnership Agreement", "Agreement defining rights and responsibilities of domestic partners."),
        ("Cohabitation Agreement", "Agreement for unmarried couples living together."),
    ]
    for name, desc in family:
        add(name, "Legal", "Family Law", "Revvel Original", "", "MD", desc, True,
            "family law, " + name.lower().replace(" ", ", "))
    
    # Business Formation
    business_formation = [
        ("LLC Operating Agreement - Single Member", "Operating agreement for a single-member LLC."),
        ("LLC Operating Agreement - Multi Member", "Operating agreement for a multi-member LLC."),
        ("Articles of Incorporation", "Document filed to create a corporation."),
        ("Corporate Bylaws", "Rules governing the internal management of a corporation."),
        ("Partnership Agreement - General", "Agreement establishing a general partnership."),
        ("Partnership Agreement - Limited", "Agreement establishing a limited partnership."),
        ("Shareholder Agreement", "Agreement among shareholders regarding company governance."),
        ("Stock Purchase Agreement", "Agreement for buying and selling company stock."),
        ("Board Resolution Template", "Template for formal board of directors resolutions."),
        ("Meeting Minutes Template", "Template for recording corporate meeting proceedings."),
        ("Certificate of Good Standing Request", "Template for requesting a certificate of good standing."),
        ("Business Name Registration (DBA)", "Doing Business As registration template."),
        ("Registered Agent Designation", "Form designating a registered agent for service of process."),
        ("Annual Report Template", "Template for filing annual corporate reports."),
        ("Dissolution Agreement", "Agreement for dissolving a business entity."),
    ]
    for name, desc in business_formation:
        add(name, "Legal", "Business Formation", "Revvel Original", "", "MD", desc, True,
            "business formation, corporate, " + name.lower().replace(" ", ", "))
    
    # Court Filings
    court = [
        ("Appellate Brief Template", "Template for briefs filed in appellate courts."),
        ("Motion to Dismiss", "Motion requesting the court dismiss a case."),
        ("Motion for Summary Judgment", "Motion arguing no genuine dispute of material fact exists."),
        ("Motion to Compel Discovery", "Motion requesting the court order discovery compliance."),
        ("Motion for Continuance", "Motion requesting postponement of a court proceeding."),
        ("Motion in Limine", "Motion to exclude certain evidence before trial."),
        ("Memorandum of Law", "Legal memorandum supporting a motion or position."),
        ("Complaint Template - Civil", "Template for filing a civil complaint."),
        ("Answer to Complaint", "Template for responding to a civil complaint."),
        ("Counterclaim Template", "Template for filing a counterclaim in civil litigation."),
        ("Interrogatories Template", "Written questions to be answered under oath during discovery."),
        ("Request for Production of Documents", "Discovery request for relevant documents."),
        ("Request for Admissions", "Discovery request asking party to admit or deny facts."),
        ("Deposition Notice", "Notice scheduling a deposition."),
        ("Subpoena Template", "Template for issuing a subpoena for testimony or documents."),
        ("Cease and Desist Letter", "Letter demanding cessation of specified activities."),
        ("Demand Letter", "Formal letter demanding payment or action."),
        ("Small Claims Court Filing", "Template for filing a small claims court action."),
        ("Pro Se Appearance Form", "Form for self-represented litigants."),
        ("Affidavit Template", "Sworn written statement for use as evidence."),
        ("Declaration Template", "Written statement made under penalty of perjury."),
        ("Stipulation and Order", "Agreement between parties submitted to the court."),
        ("Proposed Order Template", "Draft order for the judge's signature."),
    ]
    for name, desc in court:
        add(name, "Legal", "Court Filings", "Revvel Original", "", "MD", desc, True,
            "court filing, litigation, " + name.lower().replace(" ", ", "))
    
    # Employment Law
    employment = [
        ("Employment Agreement - Full Time", "Standard employment contract for full-time employees."),
        ("Employment Agreement - Part Time", "Employment contract for part-time employees."),
        ("At-Will Employment Agreement", "Employment agreement with at-will termination provisions."),
        ("Offer Letter Template", "Job offer letter with compensation and start date details."),
        ("Employee Handbook Template", "Comprehensive employee handbook covering policies and procedures."),
        ("Employee Onboarding Checklist", "Checklist for new employee orientation and setup."),
        ("Performance Review Template", "Template for conducting employee performance evaluations."),
        ("Termination Letter", "Formal letter terminating employment."),
        ("Resignation Letter", "Template for employee resignation notification."),
        ("Severance Agreement", "Agreement providing severance benefits upon termination."),
        ("Non-Compete Agreement - Employee", "Restrictive covenant for employees."),
        ("Invention Assignment Agreement", "Agreement assigning employee inventions to the employer."),
        ("Remote Work Agreement", "Agreement establishing terms for remote work arrangements."),
        ("Internship Agreement", "Agreement for unpaid or paid internship positions."),
        ("Employee Privacy Policy", "Policy governing employee data privacy and monitoring."),
        ("Workplace Safety Policy", "Policy establishing workplace safety standards and procedures."),
        ("Anti-Harassment Policy", "Policy prohibiting workplace harassment and discrimination."),
        ("Drug Testing Consent Form", "Consent form for workplace drug testing."),
        ("Background Check Authorization", "Authorization for employment background checks."),
        ("Workers Compensation Claim Form", "Form for filing workers compensation claims."),
    ]
    for name, desc in employment:
        add(name, "Legal", "Employment Law", "Revvel Original", "", "MD", desc, True,
            "employment, hr, " + name.lower().replace(" ", ", "))
    
    # Intellectual Property
    ip_templates = [
        ("Copyright Registration Application", "Application to register copyright with the US Copyright Office."),
        ("Copyright Assignment Agreement", "Agreement transferring copyright ownership."),
        ("Copyright License Agreement", "Agreement licensing copyright use to another party."),
        ("DMCA Takedown Notice", "Notice requesting removal of infringing content under DMCA."),
        ("DMCA Counter-Notification", "Response to a DMCA takedown notice."),
        ("Trademark License Agreement", "Agreement licensing trademark use."),
        ("Trade Secret Protection Policy", "Policy for protecting company trade secrets."),
        ("Work for Hire Agreement", "Agreement establishing work product as work for hire."),
        ("Content License Agreement", "Agreement licensing content for specific uses."),
        ("Open Source License Selection Guide", "Guide for choosing appropriate open source licenses."),
    ]
    for name, desc in ip_templates:
        add(name, "Legal", "Intellectual Property", "Revvel Original", "", "MD", desc, True,
            "intellectual property, copyright, trademark, " + name.lower().replace(" ", ", "))
    
    # ==========================================
    # ACADEMIC & RESEARCH TEMPLATES
    # ==========================================
    
    # Research Papers
    papers = [
        ("APA 7th Edition Research Paper", "Research paper formatted per APA 7th edition guidelines.", "Overleaf", "https://www.overleaf.com/latex/templates"),
        ("MLA 9th Edition Research Paper", "Research paper formatted per MLA 9th edition guidelines.", "Overleaf", "https://www.overleaf.com/latex/templates"),
        ("Chicago/Turabian Style Paper", "Research paper in Chicago Manual of Style format.", "Overleaf", "https://www.overleaf.com/latex/templates"),
        ("IEEE Conference Paper Template", "Template for IEEE conference paper submissions.", "IEEE", "https://www.ieee.org/conferences/publishing/templates.html"),
        ("IEEE Journal Article Template", "Template for IEEE journal article submissions.", "IEEE", "https://www.ieee.org/publications/authors/author-templates.html"),
        ("ACM Conference Paper Template", "Template for ACM conference proceedings.", "ACM", "https://www.acm.org/publications/proceedings-template"),
        ("ACM Journal Article Template", "Template for ACM journal submissions.", "ACM", "https://www.acm.org/publications/authors/submissions"),
        ("Springer Journal Template", "Template for Springer Nature journal submissions.", "Springer", "https://www.springer.com/gp/authors-editors/journal-author/journal-author-helpdesk/manuscript-preparation"),
        ("Elsevier Journal Template", "Template for Elsevier journal article submissions.", "Elsevier", "https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions"),
        ("Harvard Style Research Paper", "Research paper formatted in Harvard referencing style.", "Revvel Original", ""),
        ("SSRN Working Paper Template", "Template formatted for SSRN working paper submissions.", "SSRN", "https://www.ssrn.com"),
        ("Literature Review Template", "Structured template for conducting systematic literature reviews.", "Revvel Original", ""),
        ("Annotated Bibliography Template", "Template for creating annotated bibliographies.", "Revvel Original", ""),
        ("Case Study Template", "Template for academic case study analysis.", "Revvel Original", ""),
        ("Lab Report Template", "Scientific lab report with methods, results, and discussion sections.", "Revvel Original", ""),
        ("Book Review Template", "Template for academic book reviews.", "Revvel Original", ""),
        ("Research Proposal Template", "Template for proposing research projects.", "Revvel Original", ""),
        ("Systematic Review Protocol", "PRISMA-compliant systematic review protocol template.", "Revvel Original", ""),
        ("Meta-Analysis Template", "Template for conducting and reporting meta-analyses.", "Revvel Original", ""),
        ("Qualitative Research Template", "Template for qualitative research methodology papers.", "Revvel Original", ""),
    ]
    for name, desc, source, url in papers:
        add(name, "Academic & Research", "Research Papers", source, url, "LaTeX, DOCX", desc, True,
            "research paper, academic, " + name.lower().replace(" ", ", "))
    
    # Thesis & Dissertation
    thesis = [
        ("PhD Dissertation Template - LaTeX", "Comprehensive LaTeX template for doctoral dissertations."),
        ("Master's Thesis Template - LaTeX", "LaTeX template for master's thesis documents."),
        ("PhD Dissertation Template - Word", "Microsoft Word template for doctoral dissertations."),
        ("Master's Thesis Template - Word", "Word template for master's thesis documents."),
        ("Thesis Proposal Template", "Template for thesis/dissertation proposals."),
        ("Dissertation Defense Presentation", "Slide template for dissertation defense presentations."),
        ("Thesis Committee Approval Form", "Form for thesis committee review and approval."),
        ("Abstract Template", "Template for writing thesis/dissertation abstracts."),
    ]
    for name, desc in thesis:
        fmt = "LaTeX" if "LaTeX" in name else "DOCX"
        add(name, "Academic & Research", "Thesis & Dissertation", "Revvel Original", "", fmt, desc, True,
            "thesis, dissertation, graduate, " + name.lower().replace(" ", ", "))
    
    # Grant Proposals
    grants = [
        ("NSF Grant Proposal Template", "Template following NSF proposal formatting guidelines.", "NSF", "https://www.nsf.gov"),
        ("NIH R01 Grant Application", "Template for NIH R01 research project grant applications.", "NIH", "https://grants.nih.gov"),
        ("NIH R21 Exploratory Grant", "Template for NIH R21 exploratory/developmental research grants.", "NIH", "https://grants.nih.gov"),
        ("DOE Research Grant Template", "Template for Department of Energy research grant proposals.", "DOE", "https://www.energy.gov"),
        ("NEH Fellowship Application", "Template for National Endowment for Humanities fellowships.", "NEH", "https://www.neh.gov"),
        ("Fulbright Application Template", "Template for Fulbright scholarship applications.", "Fulbright", "https://www.fulbright.org"),
        ("Generic Grant Proposal Template", "Universal grant proposal template adaptable to any funder.", "Revvel Original", ""),
        ("Grant Budget Template", "Budget spreadsheet template for grant applications.", "Revvel Original", ""),
        ("Grant Progress Report", "Template for reporting grant-funded research progress.", "Revvel Original", ""),
        ("Letter of Support Template", "Template for letters supporting grant applications.", "Revvel Original", ""),
    ]
    for name, desc, source, url in grants:
        add(name, "Academic & Research", "Grant Proposals", source, url, "DOCX, PDF", desc, True,
            "grant, proposal, funding, " + name.lower().replace(" ", ", "))
    
    # White Papers
    whitepapers = [
        ("Government Agency White Paper", "Template for federal/state agency policy white papers."),
        ("Technology White Paper", "Template for technology company white papers."),
        ("Healthcare White Paper", "Template for healthcare industry white papers."),
        ("Financial Services White Paper", "Template for financial industry white papers."),
        ("Cybersecurity White Paper", "Template for cybersecurity policy and technical white papers."),
        ("Environmental Policy White Paper", "Template for environmental policy white papers."),
        ("Education Policy White Paper", "Template for education policy white papers."),
        ("Defense & Intelligence White Paper", "Template for defense sector white papers."),
        ("Startup White Paper", "Template for startup/venture capital white papers."),
        ("Blockchain/Crypto White Paper", "Template for cryptocurrency and blockchain project white papers."),
        ("AI/ML Research White Paper", "Template for artificial intelligence research white papers."),
        ("Public Health White Paper", "Template for public health policy white papers."),
    ]
    for name, desc in whitepapers:
        add(name, "Academic & Research", "White Papers", "Revvel Original", "", "MD, DOCX", desc, True,
            "white paper, policy, " + name.lower().replace(" ", ", "))
    
    # Academic Posters & CV
    academic_misc = [
        ("Academic Conference Poster - Portrait", "Portrait-oriented academic poster template.", "Academic Posters"),
        ("Academic Conference Poster - Landscape", "Landscape-oriented academic poster template.", "Academic Posters"),
        ("Research Poster - Scientific", "Scientific research poster with methods and results sections.", "Academic Posters"),
        ("Academic CV - Junior Faculty", "CV template for junior faculty and postdocs.", "Academic CV"),
        ("Academic CV - Senior Faculty", "CV template for tenured and senior faculty.", "Academic CV"),
        ("Academic CV - Graduate Student", "CV template for graduate students.", "Academic CV"),
        ("Academic CV - Postdoc", "CV template for postdoctoral researchers.", "Academic CV"),
        ("Teaching Portfolio Template", "Template for documenting teaching experience and philosophy.", "Academic CV"),
        ("Research Statement Template", "Template for research interest and plan statements.", "Academic CV"),
        ("Teaching Statement Template", "Template for teaching philosophy statements.", "Academic CV"),
        ("Diversity Statement Template", "Template for diversity and inclusion statements.", "Academic CV"),
    ]
    for name, desc, subcat in academic_misc:
        add(name, "Academic & Research", subcat, "Revvel Original", "", "LaTeX, DOCX", desc, True,
            "academic, " + subcat.lower().replace(" ", ", ") + ", " + name.lower().replace(" ", ", "))
    
    # ==========================================
    # BUSINESS TEMPLATES
    # ==========================================
    
    business_plans = [
        ("Lean Business Plan", "One-page lean business plan template.", "Business Plans"),
        ("Traditional Business Plan", "Comprehensive multi-section business plan template.", "Business Plans"),
        ("Startup Business Plan", "Business plan tailored for startup funding applications.", "Business Plans"),
        ("Nonprofit Business Plan", "Business plan template for nonprofit organizations.", "Business Plans"),
        ("Restaurant Business Plan", "Industry-specific business plan for restaurants.", "Business Plans"),
        ("E-Commerce Business Plan", "Business plan for online retail businesses.", "Business Plans"),
        ("SaaS Business Plan", "Business plan for Software-as-a-Service companies.", "Business Plans"),
        ("Franchise Business Plan", "Business plan for franchise operations.", "Business Plans"),
        ("Social Enterprise Business Plan", "Business plan for social impact organizations.", "Business Plans"),
        ("Business Model Canvas", "Visual business model planning template.", "Business Plans"),
        ("Value Proposition Canvas", "Template for defining value propositions.", "Business Plans"),
    ]
    
    financial = [
        ("Financial Projections Spreadsheet", "3-5 year financial projections template.", "Financial Documents"),
        ("Profit and Loss Statement", "Income statement template for tracking revenue and expenses.", "Financial Documents"),
        ("Balance Sheet Template", "Template for reporting assets, liabilities, and equity.", "Financial Documents"),
        ("Cash Flow Statement", "Template for tracking cash inflows and outflows.", "Financial Documents"),
        ("Budget Template - Annual", "Annual business budget planning template.", "Financial Documents"),
        ("Budget Template - Monthly", "Monthly budget tracking template.", "Financial Documents"),
        ("Break-Even Analysis", "Template for calculating break-even point.", "Financial Documents"),
        ("Invoice Template - Standard", "Professional invoice template for billing clients.", "Financial Documents"),
        ("Invoice Template - Freelance", "Invoice template designed for freelancers.", "Financial Documents"),
        ("Invoice Template - Hourly", "Time-based billing invoice template.", "Financial Documents"),
        ("Receipt Template", "Payment receipt template for transactions.", "Financial Documents"),
        ("Purchase Order Template", "Template for issuing purchase orders.", "Financial Documents"),
        ("Expense Report Template", "Employee expense reimbursement report.", "Financial Documents"),
        ("Accounts Receivable Aging", "Template for tracking outstanding receivables.", "Financial Documents"),
        ("Accounts Payable Tracker", "Template for managing accounts payable.", "Financial Documents"),
        ("Startup Financial Model", "Comprehensive financial model for startups.", "Financial Documents"),
        ("Cap Table Template", "Capitalization table for tracking equity ownership.", "Financial Documents"),
    ]
    
    marketing = [
        ("Marketing Plan Template", "Comprehensive marketing strategy and plan template.", "Marketing"),
        ("Social Media Strategy Template", "Template for planning social media campaigns.", "Marketing"),
        ("Content Calendar Template", "Editorial calendar for content planning.", "Marketing"),
        ("SEO Audit Template", "Template for conducting website SEO audits.", "Marketing"),
        ("Email Marketing Campaign Template", "Template for planning email marketing campaigns.", "Marketing"),
        ("Brand Guidelines Template", "Template for documenting brand identity standards.", "Marketing"),
        ("Press Release Template", "Template for writing press releases.", "Marketing"),
        ("Media Kit Template", "Template for creating media/press kits.", "Marketing"),
        ("SWOT Analysis Template", "Strategic planning template for strengths, weaknesses, opportunities, threats.", "Marketing"),
        ("Competitive Analysis Template", "Template for analyzing market competitors.", "Marketing"),
        ("Customer Persona Template", "Template for creating buyer/customer personas.", "Marketing"),
        ("Marketing Budget Template", "Template for planning marketing spend.", "Marketing"),
        ("A/B Testing Plan Template", "Template for planning and tracking A/B tests.", "Marketing"),
        ("Landing Page Copy Template", "Copywriting template for landing pages.", "Marketing"),
    ]
    
    hr = [
        ("Job Description Template", "Template for writing job descriptions.", "Human Resources"),
        ("Job Posting Template", "Template for creating job postings.", "Human Resources"),
        ("Interview Scorecard", "Template for evaluating job candidates.", "Human Resources"),
        ("Offer Letter Template", "Job offer letter template.", "Human Resources"),
        ("Employee Onboarding Checklist", "New hire onboarding process checklist.", "Human Resources"),
        ("Employee Handbook Template", "Comprehensive employee handbook.", "Human Resources"),
        ("Performance Review Template", "Employee performance evaluation form.", "Human Resources"),
        ("360-Degree Feedback Template", "Multi-rater feedback evaluation template.", "Human Resources"),
        ("Employee Satisfaction Survey", "Template for measuring employee satisfaction.", "Human Resources"),
        ("Exit Interview Template", "Questions and form for employee exit interviews.", "Human Resources"),
        ("PIP (Performance Improvement Plan)", "Template for employee performance improvement plans.", "Human Resources"),
        ("Time Off Request Form", "Employee leave/vacation request form.", "Human Resources"),
        ("Payroll Template", "Payroll processing and tracking template.", "Human Resources"),
        ("Organizational Chart Template", "Template for creating org charts.", "Human Resources"),
    ]
    
    operations = [
        ("Project Charter Template", "Template for initiating and authorizing projects.", "Operations"),
        ("Statement of Work (SOW)", "Template defining project scope, deliverables, and timeline.", "Operations"),
        ("Project Plan Template", "Comprehensive project planning template.", "Operations"),
        ("Gantt Chart Template", "Visual project timeline and task tracking.", "Operations"),
        ("Risk Assessment Template", "Template for identifying and evaluating project risks.", "Operations"),
        ("Change Request Form", "Template for requesting project changes.", "Operations"),
        ("Meeting Agenda Template", "Template for planning effective meetings.", "Operations"),
        ("Meeting Minutes Template", "Template for recording meeting proceedings.", "Operations"),
        ("Status Report Template", "Weekly/monthly project status report.", "Operations"),
        ("Lessons Learned Template", "Template for documenting project lessons learned.", "Operations"),
        ("Process Documentation Template", "Template for documenting business processes.", "Operations"),
        ("Standard Operating Procedure (SOP)", "Template for creating SOPs.", "Operations"),
        ("Business Requirements Document (BRD)", "Template for documenting business requirements.", "Operations"),
        ("Request for Proposal (RFP)", "Template for soliciting vendor proposals.", "Operations"),
        ("Request for Quotation (RFQ)", "Template for requesting price quotes.", "Operations"),
        ("Vendor Evaluation Template", "Template for evaluating and comparing vendors.", "Operations"),
    ]
    
    sales = [
        ("Sales Proposal Template", "Template for creating sales proposals.", "Sales & Proposals"),
        ("Business Proposal Template", "General business proposal template.", "Sales & Proposals"),
        ("Pitch Deck Template - Startup", "Investor pitch deck for startups.", "Sales & Proposals"),
        ("Pitch Deck Template - Series A", "Series A funding pitch deck template.", "Sales & Proposals"),
        ("Pitch Deck Template - Corporate", "Corporate presentation pitch deck.", "Sales & Proposals"),
        ("Executive Summary Template", "One-page executive summary template.", "Sales & Proposals"),
        ("Sales Forecast Template", "Template for projecting sales revenue.", "Sales & Proposals"),
        ("CRM Template", "Customer relationship management tracking template.", "Sales & Proposals"),
        ("Sales Pipeline Template", "Template for tracking sales pipeline stages.", "Sales & Proposals"),
        ("Quote Template", "Price quotation template for clients.", "Sales & Proposals"),
        ("Case Study Template - Business", "Template for creating business case studies.", "Sales & Proposals"),
        ("Testimonial Collection Template", "Template for gathering customer testimonials.", "Sales & Proposals"),
    ]
    
    for templates_list in [business_plans, financial, marketing, hr, operations, sales]:
        for item in templates_list:
            name, desc, subcat = item
            add(name, "Business", subcat, "Revvel Original", "", "MD, DOCX", desc, True,
                "business, " + subcat.lower().replace(" ", ", ") + ", " + name.lower().replace(" ", ", "))
    
    # ==========================================
    # GOVERNMENT & REGULATORY TEMPLATES
    # ==========================================
    
    gov_tax = [
        ("IRS Form W-9 Guide", "Guide and template for completing W-9 tax forms.", "IRS", "https://www.irs.gov/forms-pubs/about-form-w-9"),
        ("IRS Form W-4 Guide", "Guide for employee withholding certificate.", "IRS", "https://www.irs.gov/forms-pubs/about-form-w-4"),
        ("IRS Form 1099-NEC Guide", "Guide for nonemployee compensation reporting.", "IRS", "https://www.irs.gov/forms-pubs/about-form-1099-nec"),
        ("IRS Form 1099-MISC Guide", "Guide for miscellaneous income reporting.", "IRS", "https://www.irs.gov/forms-pubs/about-form-1099-misc"),
        ("IRS Schedule C Template", "Profit or loss from business template.", "IRS", "https://www.irs.gov/forms-pubs/about-schedule-c-form-1040"),
        ("IRS Form SS-4 (EIN Application)", "Application for Employer Identification Number.", "IRS", "https://www.irs.gov/forms-pubs/about-form-ss-4"),
        ("Quarterly Tax Estimation Worksheet", "Template for estimating quarterly tax payments.", "Revvel Original", ""),
        ("Tax Deduction Tracker", "Template for tracking business tax deductions.", "Revvel Original", ""),
        ("Home Office Deduction Calculator", "Template for calculating home office tax deductions.", "Revvel Original", ""),
        ("Mileage Log Template", "IRS-compliant mileage tracking template.", "Revvel Original", ""),
    ]
    
    gov_business = [
        ("SBA Business Plan Template", "SBA-recommended business plan format.", "SBA", "https://www.sba.gov/business-guide/plan-your-business/write-your-business-plan"),
        ("SBA Loan Application Guide", "Guide for SBA loan application process.", "SBA", "https://www.sba.gov/funding-programs/loans"),
        ("State Business Registration Template", "Template for state business entity registration.", "Revvel Original", ""),
        ("DBA (Doing Business As) Filing", "Template for filing a DBA/fictitious business name.", "Revvel Original", ""),
        ("Business License Application Guide", "Guide for obtaining business licenses.", "Revvel Original", ""),
        ("Seller's Permit Application Guide", "Guide for obtaining a seller's permit.", "Revvel Original", ""),
        ("EIN Application Walkthrough", "Step-by-step guide for obtaining an EIN.", "Revvel Original", ""),
    ]
    
    gov_ip = [
        ("USPTO Patent Application Template", "Template for utility patent applications.", "USPTO", "https://www.uspto.gov/patents/basics"),
        ("USPTO Provisional Patent Application", "Template for provisional patent applications.", "USPTO", "https://www.uspto.gov/patents/basics/types-patent-applications/provisional-application-patent"),
        ("USPTO Trademark Application Guide", "Guide for filing trademark applications.", "USPTO", "https://www.uspto.gov/trademarks/basics"),
        ("Patent Specification Template", "Template for writing patent specifications.", "Revvel Original", ""),
        ("Patent Claims Template", "Template for drafting patent claims.", "Revvel Original", ""),
        ("Trademark Specimen Guide", "Guide for submitting trademark specimens.", "Revvel Original", ""),
        ("Design Patent Application", "Template for design patent applications.", "USPTO", "https://www.uspto.gov/patents/basics/types-patent-applications/design-patent-application-guide"),
    ]
    
    gov_foia = [
        ("FOIA Request Letter - Federal", "Template for federal Freedom of Information Act requests.", "FOIA.gov", "https://www.foia.gov"),
        ("FOIA Request Letter - State", "Template for state-level public records requests.", "Revvel Original", ""),
        ("FOIA Appeal Letter", "Template for appealing FOIA request denials.", "Revvel Original", ""),
        ("Public Records Request Template", "General template for public records requests.", "Revvel Original", ""),
        ("FOIA Fee Waiver Request", "Template for requesting FOIA fee waivers.", "Revvel Original", ""),
    ]
    
    gov_contracts = [
        ("GSA Schedule Contract Template", "Template for GSA schedule contract proposals.", "GSA", "https://www.gsa.gov"),
        ("Government Contract Proposal Template", "Template for federal contract proposals.", "Revvel Original", ""),
        ("SAM.gov Registration Guide", "Guide for registering on SAM.gov.", "SAM.gov", "https://sam.gov"),
        ("Capability Statement Template", "One-page capability statement for government contracting.", "Revvel Original", ""),
        ("Past Performance Reference Template", "Template for documenting past performance.", "Revvel Original", ""),
        ("Small Business Subcontracting Plan", "Template for small business subcontracting plans.", "Revvel Original", ""),
    ]
    
    gov_grants = [
        ("Federal Grant Application Template", "Template for federal grant applications.", "Grants.gov", "https://www.grants.gov"),
        ("State Grant Application Template", "Template for state-level grant applications.", "Revvel Original", ""),
        ("Grant Budget Narrative Template", "Template for grant budget justifications.", "Revvel Original", ""),
        ("Grant Logic Model Template", "Template for creating program logic models.", "Revvel Original", ""),
        ("Grant Evaluation Plan Template", "Template for grant program evaluation plans.", "Revvel Original", ""),
        ("Community Development Block Grant", "Template for CDBG applications.", "HUD", "https://www.hud.gov"),
    ]
    
    gov_compliance = [
        ("OSHA Safety Plan Template", "Workplace safety plan per OSHA requirements.", "OSHA", "https://www.osha.gov"),
        ("Environmental Impact Assessment", "Template for environmental impact assessments.", "EPA", "https://www.epa.gov"),
        ("ADA Compliance Checklist", "Checklist for Americans with Disabilities Act compliance.", "Revvel Original", ""),
        ("HIPAA Compliance Checklist", "Checklist for HIPAA healthcare data compliance.", "Revvel Original", ""),
        ("GDPR Compliance Template", "Template for GDPR data protection compliance.", "Revvel Original", ""),
        ("SEC Filing Template Guide", "Guide for SEC regulatory filings.", "SEC", "https://www.sec.gov"),
        ("FCC Filing Template Guide", "Guide for FCC regulatory filings.", "FCC", "https://www.fcc.gov"),
        ("FDA Submission Guide", "Guide for FDA product submission process.", "FDA", "https://www.fda.gov"),
        ("SOX Compliance Checklist", "Sarbanes-Oxley Act compliance checklist.", "Revvel Original", ""),
        ("PCI DSS Compliance Checklist", "Payment Card Industry compliance checklist.", "Revvel Original", ""),
        ("CCPA Privacy Policy Template", "California Consumer Privacy Act policy template.", "Revvel Original", ""),
        ("Privacy Policy Template", "General website/app privacy policy template.", "Revvel Original", ""),
        ("Terms of Service Template", "Website/app terms of service template.", "Revvel Original", ""),
        ("Cookie Policy Template", "Website cookie policy template.", "Revvel Original", ""),
        ("Data Processing Agreement", "GDPR-compliant data processing agreement.", "Revvel Original", ""),
    ]
    
    for templates_list, subcat in [
        (gov_tax, "Tax & IRS"), (gov_business, "Business Registration"),
        (gov_ip, "Patents & Trademarks"), (gov_foia, "FOIA & Public Records"),
        (gov_contracts, "Government Contracts"), (gov_grants, "Government Grants"),
        (gov_compliance, "Regulatory Compliance")
    ]:
        for item in templates_list:
            if len(item) == 4:
                name, desc, source, url = item
            else:
                name, desc = item
                source, url = "Revvel Original", ""
            add(name, "Government & Regulatory", subcat, source, url, "MD, PDF", desc, True,
                "government, regulatory, " + subcat.lower().replace(" ", ", ") + ", " + name.lower().replace(" ", ", "))
    
    # ==========================================
    # FOSS & DEVELOPER TEMPLATES
    # ==========================================
    
    github_templates = [
        ("README.md Template - Standard", "Comprehensive README template for open source projects."),
        ("README.md Template - Minimal", "Minimal README template for small projects."),
        ("README.md Template - Awesome List", "README template for awesome-list style repositories."),
        ("CONTRIBUTING.md Template", "Template for contribution guidelines."),
        ("CODE_OF_CONDUCT.md Template", "Code of conduct based on Contributor Covenant."),
        ("SECURITY.md Template", "Security policy and vulnerability reporting template."),
        ("CHANGELOG.md Template", "Changelog following Keep a Changelog format."),
        ("Pull Request Template", "Template for standardizing pull request descriptions."),
        ("Bug Report Issue Template", "GitHub issue template for bug reports."),
        ("Feature Request Issue Template", "GitHub issue template for feature requests."),
        ("GitHub Actions Workflow - CI", "CI workflow template for GitHub Actions."),
        ("GitHub Actions Workflow - CD", "Deployment workflow template for GitHub Actions."),
        ("GitHub Actions Workflow - Release", "Automated release workflow template."),
        (".gitignore Collection", "Comprehensive .gitignore templates for various languages."),
        ("LICENSE File Templates", "Collection of common open source license files."),
        ("CODEOWNERS Template", "Template for defining code ownership."),
        ("Dependabot Configuration", "Template for Dependabot dependency updates."),
        ("GitHub Pages Configuration", "Template for GitHub Pages site configuration."),
    ]
    
    docs_templates = [
        ("API Documentation Template", "Template for RESTful API documentation."),
        ("Technical Documentation Template", "Template for software technical documentation."),
        ("Architecture Decision Record (ADR)", "Template for recording architecture decisions."),
        ("Software Requirements Specification", "IEEE-style SRS document template."),
        ("Software Design Document", "Template for software design specifications."),
        ("User Guide Template", "Template for end-user documentation."),
        ("Developer Guide Template", "Template for developer onboarding documentation."),
        ("Runbook Template", "Operational runbook for system procedures."),
        ("Incident Response Template", "Template for documenting incident response."),
        ("Postmortem Template", "Blameless postmortem analysis template."),
        ("RFC (Request for Comments) Template", "Template for proposing technical changes."),
        ("Technical Blog Post Template", "Template for writing technical blog posts."),
        ("Release Notes Template", "Template for software release notes."),
        ("Migration Guide Template", "Template for documenting migration procedures."),
        ("Troubleshooting Guide Template", "Template for troubleshooting documentation."),
    ]
    
    devops_templates = [
        ("Dockerfile Template", "Best-practice Dockerfile for containerized applications."),
        ("Docker Compose Template", "Multi-service Docker Compose configuration."),
        ("Kubernetes Deployment Template", "K8s deployment manifest template."),
        ("Kubernetes Service Template", "K8s service manifest template."),
        ("Helm Chart Template", "Helm chart scaffolding template."),
        ("Terraform Module Template", "Terraform infrastructure module template."),
        ("Ansible Playbook Template", "Ansible automation playbook template."),
        ("CI/CD Pipeline Template - Jenkins", "Jenkinsfile pipeline template."),
        ("CI/CD Pipeline Template - GitLab", "GitLab CI/CD configuration template."),
        ("Nginx Configuration Template", "Nginx web server configuration template."),
        ("Monitoring Dashboard Template", "Grafana/Prometheus dashboard template."),
        ("Alert Rules Template", "Monitoring alert rules template."),
        ("Infrastructure as Code Template", "Generic IaC project structure template."),
    ]
    
    security_templates = [
        ("Security Policy Template", "Organization security policy template."),
        ("Incident Response Plan", "Cybersecurity incident response plan template."),
        ("Vulnerability Disclosure Policy", "Responsible vulnerability disclosure template."),
        ("Security Audit Checklist", "Application security audit checklist."),
        ("Penetration Testing Report", "Penetration test findings report template."),
        ("Risk Assessment Matrix", "Security risk assessment and scoring template."),
        ("Business Continuity Plan", "Template for business continuity planning."),
        ("Disaster Recovery Plan", "IT disaster recovery plan template."),
        ("Data Classification Policy", "Template for data classification standards."),
        ("Access Control Policy", "Template for access control procedures."),
        ("Encryption Policy", "Template for data encryption standards."),
        ("Security Awareness Training Plan", "Template for security training programs."),
    ]
    
    project_templates = [
        ("Open Source Project Governance", "Template for open source project governance."),
        ("Contributor License Agreement (CLA)", "Template for contributor license agreements."),
        ("Project Roadmap Template", "Template for open source project roadmaps."),
        ("Community Guidelines Template", "Template for community interaction guidelines."),
        ("Maintainer Guide Template", "Guide template for project maintainers."),
        ("Release Checklist Template", "Checklist for software releases."),
        ("Sprint Planning Template", "Agile sprint planning template."),
        ("Retrospective Template", "Sprint/project retrospective template."),
        ("User Story Template", "Agile user story writing template."),
        ("Technical Debt Tracker", "Template for tracking and prioritizing technical debt."),
    ]
    
    for templates_list, subcat in [
        (github_templates, "GitHub Templates"), (docs_templates, "Documentation"),
        (devops_templates, "DevOps & Infrastructure"), (security_templates, "Security"),
        (project_templates, "Project Management")
    ]:
        for name, desc in templates_list:
            add(name, "FOSS & Developer", subcat, "Revvel Original", "", "MD", desc, True,
                "developer, foss, " + subcat.lower().replace(" ", ", ") + ", " + name.lower().replace(" ", ", "))
    
    # ==========================================
    # PERSONAL & FINANCE TEMPLATES
    # ==========================================
    
    personal = [
        ("Personal Budget Template", "Monthly personal budget tracking template.", "Personal Finance"),
        ("Debt Payoff Tracker", "Template for tracking debt repayment progress.", "Personal Finance"),
        ("Net Worth Calculator", "Template for calculating personal net worth.", "Personal Finance"),
        ("Investment Portfolio Tracker", "Template for tracking investment holdings.", "Personal Finance"),
        ("Retirement Planning Calculator", "Template for retirement savings planning.", "Personal Finance"),
        ("Emergency Fund Tracker", "Template for building emergency savings.", "Personal Finance"),
        ("Wedding Budget Template", "Budget planning template for weddings.", "Life Events"),
        ("Moving Checklist", "Comprehensive moving and relocation checklist.", "Life Events"),
        ("Travel Planning Template", "Trip planning and itinerary template.", "Life Events"),
        ("Home Buying Checklist", "Checklist for the home buying process.", "Life Events"),
        ("Resume Template - Professional", "Professional resume/CV template.", "Career"),
        ("Resume Template - Creative", "Creative resume design template.", "Career"),
        ("Resume Template - Technical", "Technical/engineering resume template.", "Career"),
        ("Cover Letter Template", "Job application cover letter template.", "Career"),
        ("Thank You Letter - Interview", "Post-interview thank you letter template.", "Career"),
        ("Reference Letter Template", "Professional reference letter template.", "Career"),
        ("Letter of Recommendation", "Academic/professional recommendation letter.", "Career"),
        ("Personal Letter Template", "Formal personal letter template.", "Correspondence"),
        ("Complaint Letter Template", "Formal complaint letter template.", "Correspondence"),
        ("Apology Letter Template", "Formal apology letter template.", "Correspondence"),
    ]
    for name, desc, subcat in personal:
        add(name, "Personal & Finance", subcat, "Revvel Original", "", "MD, DOCX", desc, True,
            "personal, " + subcat.lower().replace(" ", ", ") + ", " + name.lower().replace(" ", ", "))
    
    return templates

def merge_research_data(templates):
    """Merge in the research data from parallel collection."""
    research_files = [
        "/home/ubuntu/templates_json/0_dKndMfFmpyjea9foXsLwB0_1771092033496_na1fn_L2hvbWUvdWJ1bnR1L2xlZ2FsX3RlbXBsYXRlcw.json",
        "/home/ubuntu/templates_json/1_mBKjKFKsAFJfzU8C4Q07kC_1771091789387_na1fn_L2hvbWUvdWJ1bnR1L3RlbXBsYXRlcw.json",
        "/home/ubuntu/templates_json/2_dv0CA2WSo3TTjlci2iHdFA_1771091932233_na1fn_L2hvbWUvdWJ1bnR1L3RlbXBsYXRlcw.json",
        "/home/ubuntu/templates_json/3_cgc7UhlAic6Y9MIoXK5xIc_1771091766687_na1fn_L2hvbWUvdWJ1bnR1L3RlbXBsYXRlcw.json",
        "/home/ubuntu/templates_json/4_7mstQE04ewHlHXcbmYkoRJ_1771093604695_na1fn_L2hvbWUvdWJ1bnR1L3RlbXBsYXRlcw.json",
    ]
    
    existing_names = {t["name"].lower() for t in templates}
    added = 0
    
    for filepath in research_files:
        if not os.path.exists(filepath):
            continue
        entries = parse_json_file(filepath)
        for entry in entries:
            name = entry.get("name", "")
            if name.lower() in existing_names:
                continue
            existing_names.add(name.lower())
            templates.append({
                "id": str(uuid.uuid4())[:8],
                "name": name,
                "category": entry.get("category", "Uncategorized"),
                "subcategory": entry.get("subcategory", ""),
                "source": entry.get("source", "Unknown"),
                "source_url": entry.get("source_url", ""),
                "download_url": entry.get("download_url", ""),
                "format": entry.get("format", "MD"),
                "description": entry.get("description", ""),
                "is_free": 1 if entry.get("is_free", True) else 0,
                "tags": entry.get("tags", ""),
                "file_path": "",
                "has_file": 0,
                "created_at": datetime.now().isoformat(),
                "popularity": 0,
                "author": "Walter-Evans",
                "seo_keywords": entry.get("tags", "")
            })
            added += 1
    
    print(f"Merged {added} additional templates from research data")
    return templates

def main():
    print("Building comprehensive template catalog...")
    
    # Create database
    conn = create_database()
    insert_categories(conn)
    insert_sources(conn)
    
    # Generate comprehensive templates
    templates = generate_comprehensive_templates()
    print(f"Generated {len(templates)} templates from comprehensive catalog")
    
    # Merge research data
    templates = merge_research_data(templates)
    print(f"Total templates after merge: {len(templates)}")
    
    # Insert into database
    c = conn.cursor()
    for t in templates:
        c.execute("""
            INSERT INTO templates (id, name, category, subcategory, source, source_url, 
                download_url, format, description, is_free, tags, file_path, has_file, 
                created_at, popularity, author, seo_keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["id"], t["name"], t["category"], t["subcategory"], t["source"],
            t["source_url"], t.get("download_url", ""), t["format"], t["description"],
            t["is_free"], t["tags"], t.get("file_path", ""), t.get("has_file", 0),
            t.get("created_at", datetime.now().isoformat()), t.get("popularity", 0),
            t.get("author", "Walter-Evans"), t.get("seo_keywords", t["tags"])
        ))
    
    # Insert into FTS index
    for t in templates:
        c.execute("""
            INSERT INTO templates_fts (name, description, tags, category, subcategory)
            VALUES (?, ?, ?, ?, ?)
        """, (t["name"], t["description"], t["tags"], t["category"], t["subcategory"]))
    
    conn.commit()
    
    # Export to JSON
    with open(CATALOG_JSON, 'w') as f:
        json.dump(templates, f, indent=2)
    
    # Print stats
    c.execute("SELECT category, COUNT(*) FROM templates GROUP BY category ORDER BY COUNT(*) DESC")
    print("\n=== Template Catalog Statistics ===")
    total = 0
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]} templates")
        total += row[1]
    print(f"  TOTAL: {total} templates")
    
    c.execute("SELECT COUNT(DISTINCT subcategory) FROM templates")
    print(f"  Subcategories: {c.fetchone()[0]}")
    
    c.execute("SELECT COUNT(DISTINCT source) FROM templates")
    print(f"  Sources: {c.fetchone()[0]}")
    
    conn.close()
    print(f"\nDatabase saved to: {DB_PATH}")
    print(f"JSON catalog saved to: {CATALOG_JSON}")

if __name__ == "__main__":
    main()
