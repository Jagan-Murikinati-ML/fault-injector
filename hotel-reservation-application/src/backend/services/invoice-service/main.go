package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "time"

    "github.com/gorilla/mux"
)

type BookingDetails struct {
    MessageVersion     string             `json:"message_version"`
    EventType          string             `json:"event_type"`
    Timestamp          string             `json:"timestamp"`
    SourceService      string             `json:"source_service"`
    BookingID          int                `json:"booking_id"`
    HotelID            string             `json:"hotel_id"`
    UserID             string             `json:"user_id"`
    CheckinDate        string             `json:"checkin_date"`
    CheckoutDate       string             `json:"checkout_date"`
    TotalNights        int                `json:"total_nights"`
    TotalGuests        int                `json:"total_guests"`
    TotalAmount        float64            `json:"total_amount"`
    Currency           string             `json:"currency"`
    BookingStatus      string             `json:"booking_status"`
    GuestDetails       GuestDetails       `json:"guest_details"`
    SpecialRequests    *string            `json:"special_requests"`
    Rooms              []Room             `json:"rooms"`
    CancellationPolicy CancellationPolicy `json:"cancellation_policy"`
}

type GuestDetails struct {
    GuestName  string  `json:"guest_name"`
    GuestEmail string  `json:"guest_email"`
    GuestPhone *string `json:"guest_phone"`
}

type Room struct {
    RoomTypeCode           string  `json:"room_type_code"`
    BookingDate            string  `json:"booking_date"`
    RoomsCount             int     `json:"rooms_count"`
    CostPerRoomPerNight    float64 `json:"cost_per_room_per_night"`
}

type CancellationPolicy struct {
    CancellationPolicyType     string  `json:"cancellation_policy_type"`
    FreeCancellationHours      int     `json:"free_cancellation_hours"`
    CancellationFeePercentage  float64 `json:"cancellation_fee_percentage"`
    RefundPolicy               string  `json:"refund_policy"`
}

type InvoiceResponse struct {
    Success     bool        `json:"success"`
    InvoiceID   string      `json:"invoice_id"`
    InvoiceData interface{} `json:"invoice_data"`
    Message     string      `json:"message"`
}

func generateInvoice(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    var booking BookingDetails
    if err := json.NewDecoder(r.Body).Decode(&booking); err != nil {
        http.Error(w, "Invalid JSON", http.StatusBadRequest)
        return
    }

    // Generate invoice ID (moved from booking service)
    invoiceID := fmt.Sprintf("INV-%d-%s-%s", 
        time.Now().Year(), 
        booking.UserID, 
        time.Now().Format("010215040"))

    // Calculate line items
    var lineItems []map[string]interface{}
    for _, room := range booking.Rooms {
        lineItem := map[string]interface{}{
            "description": fmt.Sprintf("%s Room - %s", room.RoomTypeCode, room.BookingDate),
            "quantity":    room.RoomsCount,
            "rate":        room.CostPerRoomPerNight,
            "amount":      float64(room.RoomsCount) * room.CostPerRoomPerNight,
        }
        lineItems = append(lineItems, lineItem)
    }

    // Calculate cancellation deadline
    checkinTime, _ := time.Parse("2006-01-02", booking.CheckinDate)
    cancellationDeadline := checkinTime.Add(-time.Duration(booking.CancellationPolicy.FreeCancellationHours) * time.Hour)

    // Generate complete invoice data (moved from booking service)
    invoiceData := map[string]interface{}{
        "invoice_header": map[string]interface{}{
            "invoice_number":  invoiceID,
            "invoice_date":    time.Now().Format("2006-01-02"),
            "due_date":        time.Now().Format("2006-01-02"),
            "hotel_name":      booking.HotelID, // TODO: Get actual hotel name
            "hotel_address":   "Hotel Address", // TODO: Get actual hotel address
        },
        "customer_details": map[string]interface{}{
            "guest_name":  booking.GuestDetails.GuestName,
            "guest_email": booking.GuestDetails.GuestEmail,
            "guest_phone": booking.GuestDetails.GuestPhone,
        },
        "booking_details": map[string]interface{}{
            "booking_id":     booking.BookingID,
            "checkin_date":   booking.CheckinDate,
            "checkout_date":  booking.CheckoutDate,
            "total_nights":   booking.TotalNights,
            "total_guests":   booking.TotalGuests,
        },
        "line_items": lineItems,
        "charges_summary": map[string]interface{}{
            "subtotal":     booking.TotalAmount,
            "service_tax":  0.00, // TODO: Calculate actual taxes
            "gst":          0.00, // TODO: Calculate actual taxes
            "total_amount": booking.TotalAmount,
            "currency":     booking.Currency,
        },
        "payment_details": map[string]interface{}{
            "payment_method":    "Credit Card", // TODO: Get from request
            "payment_status":    "PAID",
            "payment_reference": nil, // TODO: Get from payment gateway
        },
        "cancellation_policy": map[string]interface{}{
            "policy_type":                booking.CancellationPolicy.CancellationPolicyType,
            "free_cancellation_hours":    booking.CancellationPolicy.FreeCancellationHours,
            "cancellation_fee_percentage": booking.CancellationPolicy.CancellationFeePercentage,
            "cancellation_deadline":      cancellationDeadline.Format("2006-01-02T15:04:05Z07:00"),
            "refund_policy":              booking.CancellationPolicy.RefundPolicy,
            "terms": []string{
                fmt.Sprintf("Free cancellation until %d hours before check-in", booking.CancellationPolicy.FreeCancellationHours),
                "No refund for no-shows",
                "Refund will be processed within 5-7 business days",
            },
        },
    }

    response := InvoiceResponse{
        Success:     true,
        InvoiceID:   invoiceID,
        InvoiceData: invoiceData,
        Message:     "Invoice generated successfully",
    }

    json.NewEncoder(w).Encode(response)
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "status":  "healthy",
        "service": "invoice-service",
        "time":    time.Now().Format(time.RFC3339),
    })
}

func main() {
    r := mux.NewRouter()

    // Routes
    r.HandleFunc("/health", healthCheck).Methods("GET")
    r.HandleFunc("/invoice/generate", generateInvoice).Methods("POST")

    // Get port from environment
    port := os.Getenv("PORT")
    if port == "" {
        port = "8003"
    }

    log.Printf("Invoice service starting on port %s", port)
    log.Fatal(http.ListenAndServe(":"+port, r))
}
