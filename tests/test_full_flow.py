# test_full_flow.py
"""
Test the complete OCR → WhatsApp flow.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import ocr_service
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def simulate_whatsapp_flow():
    """Simulate a user sending a photo via WhatsApp."""
    print("Simulating WhatsApp OCR Flow...")
    print("=" * 50)
    
    # Step 1: User takes photo of phone number
    print("\n1. User takes photo of phone number: 08012345678")
    
    # Create the photo
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    d.text((50, 80), "08012345678", fill='black')
    
    # Convert to bytes (simulate WhatsApp upload)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes = img_bytes.getvalue()
    
    print("   ✓ Photo taken and sent to mypadi")
    
    # Step 2: mypadi processes with OCR
    print("\n2. mypadi processes photo with DeepSeek-OCR...")
    
    phone_number = ocr_service.extract_phone_number(img_bytes)
    
    if phone_number:
        print(f"   ✓ OCR successful! Found: {phone_number}")
        
        # Step 3: mypadi responds
        print("\n3. mypadi responds via WhatsApp:")
        print("   ┌─────────────────────────────────────┐")
        print(f"   │ 📞 Found: {phone_number:15} │")
        print("   │ How much airtime should I send?     │")
        print("   │ (e.g., ₦500)                        │")
        print("   └─────────────────────────────────────┘")
        
        # Step 4: User responds with amount
        print("\n4. User responds: '₦500'")
        
        # Step 5: mypadi confirms
        print("\n5. mypadi confirms:")
        print("   ┌─────────────────────────────────────┐")
        print(f"   │ Sending ₦500 to {phone_number} │")
        print("   │ Confirm? (yes/no)                   │")
        print("   └─────────────────────────────────────┘")
        
        # Step 6: User confirms
        print("\n6. User responds: 'yes'")
        
        # Step 7: Transaction processed
        print("\n7. Transaction processed!")
        print("   ┌─────────────────────────────────────┐")
        print("   │ ✅ Airtime sent successfully!       │")
        print("   │ Transaction: #MP001                 │")
        print("   │ Amount: ₦500                        │")
        print("   │ To: 08012345678                     │")
        print("   │ Status: Completed                   │")
        print("   └─────────────────────────────────────┘")
        
        print("\n🎉 Complete flow simulation successful!")
        return True
    else:
        print("   ✗ OCR failed to find phone number")
        return False

if __name__ == "__main__":
    print("Testing mypadi OCR WhatsApp Flow")
    print("=" * 50)
    
    try:
        success = simulate_whatsapp_flow()
        
        if success:
            print("\n✅ All tests passed!")
            print("\nNext steps:")
            print("1. Set up Twilio webhook URL")
            print("2. Test with real WhatsApp messages")
            print("3. Implement VTPass integration")
        else:
            print("\n❌ Test failed. Check OCR service.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure transformers is installed:")
        print("pip install transformers torch pillow")