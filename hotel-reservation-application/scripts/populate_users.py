import requests
import json
from datetime import date

# API endpoint
AUTH_API_URL = "http://localhost:9000/auth/signup"

# Sample users data
users_data = [
    {
        'username': 'arjun_singh',
        'email': 'arjun.singh@email.com',
        'password': 'password123',
        'firstName': 'Arjun',
        'lastName': 'Singh',
        'dateOfBirth': '1990-05-15'
    },
    {
        'username': 'priya_sharma',
        'email': 'priya.sharma@email.com',
        'password': 'password123',
        'firstName': 'Priya',
        'lastName': 'Sharma',
        'dateOfBirth': '1988-08-22'
    },
    {
        'username': 'vikram_patel',
        'email': 'vikram.patel@email.com',
        'password': 'password123',
        'firstName': 'Vikram',
        'lastName': 'Patel',
        'dateOfBirth': '1992-12-03'
    },
    {
        'username': 'ananya_reddy',
        'email': 'ananya.reddy@email.com',
        'password': 'password123',
        'firstName': 'Ananya',
        'lastName': 'Reddy',
        'dateOfBirth': '1985-03-18'
    },
    {
        'username': 'rohit_kumar',
        'email': 'rohit.kumar@email.com',
        'password': 'password123',
        'firstName': 'Rohit',
        'lastName': 'Kumar',
        'dateOfBirth': '1991-07-09'
    },
    {
        'username': 'kavya_nair',
        'email': 'kavya.nair@email.com',
        'password': 'password123',
        'firstName': 'Kavya',
        'lastName': 'Nair',
        'dateOfBirth': '1993-11-27'
    },
    {
        'username': 'sarah_wilson',
        'email': 'sarah.wilson@email.com',
        'password': 'password123',
        'firstName': 'Sarah',
        'lastName': 'Wilson',
        'dateOfBirth': '1987-04-14'
    },
    {
        'username': 'mike_chen',
        'email': 'mike.chen@email.com',
        'password': 'password123',
        'firstName': 'Mike',
        'lastName': 'Chen',
        'dateOfBirth': '1989-09-06'
    },
    {
        'username': 'deepika_gupta',
        'email': 'deepika.gupta@email.com',
        'password': 'password123',
        'firstName': 'Deepika',
        'lastName': 'Gupta',
        'dateOfBirth': '1994-01-12'
    },
    {
        'username': 'alex_johnson',
        'email': 'alex.johnson@email.com',
        'password': 'password123',
        'firstName': 'Alex',
        'lastName': 'Johnson',
        'dateOfBirth': '1986-06-30'
    }
]

def populate_users():
    success_count = 0
    error_count = 0
    
    print("Creating users via Authentication API...")
    print("=" * 50)
    
    for user in users_data:
        try:
            response = requests.post(
                AUTH_API_URL,
                headers={'Content-Type': 'application/json'},
                json=user,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Created: {user['firstName']} {user['lastName']} ({user['email']})")
                success_count += 1
            else:
                error_data = response.json()
                print(f"❌ Failed: {user['email']} - {error_data.get('message', 'Unknown error')}")
                error_count += 1
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error for {user['email']}: {e}")
            error_count += 1
        except Exception as e:
            print(f"❌ Error for {user['email']}: {e}")
            error_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully created: {success_count} users")
    print(f"❌ Failed: {error_count} users")
    print(f"📊 Total processed: {len(users_data)} users")

if __name__ == "__main__":
    populate_users()
