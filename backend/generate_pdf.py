from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_pdf(filename="company_policy.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    text = c.beginText(50, 750)
    text.setFont("Helvetica-Bold", 16)
    text.textLine("SAMSUNG. OFFICIAL COMPANY POLICY")
    text.setFont("Helvetica", 11)
    text.textLine("")
    
    sections = [
        "1. RETURN & REFUND POLICY",
        "- Items can be returned within 30 days of delivery for a full refund.",
        "- Products must be in original packaging with all included accessories.",
        "- A 15% restocking fee applies to opened laptops and desktop computers.",
        "- Return shipping is free for defective items; customer pays $5.99 otherwise.",
        "- Refunds are processed back to the original payment method within 5-7 business days.",
        "",
        "2. SHIPPING & DELIVERY",
        "- Free standard shipping on orders over $50 (delivery in 3 to 5 business days).",
        "- Expedited 2-day shipping is available at checkout for $14.99.",
        "- We currently ship only to the United States and Canada. No international shipping.",
        "- Orders placed after 2:00 PM EST ship the next business day.",
        "",
        "3. WARRANTY & REPAIRS",
        "- All hardware includes a 1-year limited manufacturer warranty.",
        "- Warranty covers internal component defects and hardware failure.",
        "- Accidental damage, cracked screens, and liquid spills are NOT covered.",
        "- Extended protection plans (TechNova Care) must be purchased within 14 days of order.",
        "",
        "4. SUPPORT HOURS & CONTACT",
        "- Support hours: Monday to Friday, 9:00 AM to 6:00 PM EST.",
        "- Support is closed on US federal holidays.",
        "- Official support email: support@technova.com | Toll-Free: 1-800-555-0199.",
    ]
    
    for line in sections:
        if line.startswith(("1.", "2.", "3.", "4.")):
            text.setFont("Helvetica-Bold", 12)
            text.textLine(line)
            text.setFont("Helvetica", 11)
        else:
            text.textLine(line)
            
    c.drawText(text)
    c.save()
    print(f"Created '{filename}' successfully!")

if __name__ == "__main__":
    create_sample_pdf()