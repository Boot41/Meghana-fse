import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict, List
from datetime import datetime
import pdfkit

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

    def generate_itinerary_pdf(self, itinerary_data: Dict) -> bytes:
        """Generate a PDF from the itinerary data."""
        try:
            # Create HTML content
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ text-align: center; padding: 20px; background-color: #f5f5f5; }}
                    .day-plan {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                    .activity {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; }}
                    .weather {{ color: #666; }}
                    .tips {{ margin-top: 30px; padding: 15px; background-color: #f5f5f5; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Your Travel Itinerary</h1>
                    <p>Destination: {itinerary_data.get('destination', '')}</p>
                    <p>{itinerary_data.get('weather_summary', '')}</p>
                </div>

                <div class="summary">
                    <h2>Trip Summary</h2>
                    <p>{itinerary_data.get('summary', '')}</p>
                </div>
            """

            # Add each day's itinerary
            for day in itinerary_data.get('itinerary', []):
                html_content += f"""
                <div class="day-plan">
                    <h3>Day {day['day']}</h3>
                    <div class="weather">
                        Weather: {day.get('weather', {}).get('condition', '')}
                        Temperature: {day.get('weather', {}).get('temperature', '')}°C
                    </div>
                """
                
                for activity in day.get('activities', []):
                    html_content += f"""
                    <div class="activity">
                        <h4>{activity['time']} - {activity['name']}</h4>
                        <p>{activity['description']}</p>
                        <p class="weather">{activity.get('weather_note', '')}</p>
                    </div>
                    """
                
                html_content += "</div>"

            # Add travel tips
            if itinerary_data.get('tips'):
                html_content += """
                <div class="tips">
                    <h2>Travel Tips</h2>
                    <ul>
                """
                for tip in itinerary_data['tips']:
                    html_content += f"<li>{tip}</li>"
                html_content += "</ul></div>"

            html_content += "</body></html>"

            # Convert HTML to PDF
            pdf_content = pdfkit.from_string(html_content, False)
            return pdf_content

        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            raise

    def send_itinerary_email(self, email: str, itinerary_data: Dict) -> bool:
        """Send itinerary as PDF to the specified email."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = f"Your Travel Itinerary for {itinerary_data.get('destination', 'Your Trip')}"
            msg['From'] = self.smtp_username
            msg['To'] = email

            # Add body
            body = f"""
            Hello!

            Thank you for using our travel planning service. Attached is your personalized travel itinerary for {itinerary_data.get('destination', 'your trip')}.

            The PDF includes:
            - Detailed day-by-day itinerary
            - Weather information
            - Activity recommendations
            - Travel tips

            Have a great trip!

            Best regards,
            Your Travel Assistant
            """
            msg.attach(MIMEText(body, 'plain'))

            # Generate and attach PDF
            pdf_content = self.generate_itinerary_pdf(itinerary_data)
            pdf_attachment = MIMEApplication(pdf_content, _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                    filename=f"travel_itinerary_{datetime.now().strftime('%Y%m%d')}.pdf")
            msg.attach(pdf_attachment)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            print(f"Successfully sent itinerary to {email}")
            return True

        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
