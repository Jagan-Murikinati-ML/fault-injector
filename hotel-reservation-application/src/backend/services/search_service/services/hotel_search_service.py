from elasticsearch import Elasticsearch
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class HotelSearchService:
    def __init__(self, es_client: Elasticsearch):
        self.es = es_client
        self.index_name = "hotels"
    
    async def search_hotels(self, city=None, checkin=None, checkout=None, guests=None, min_price=None, max_price=None, amenities=None) -> Dict:
        """Search hotels with filters and sorting"""
        print("=== SEARCH_HOTELS FUNCTION CALLED ===")
        print(f"Parameters: city={city}, checkin={checkin}, checkout={checkout}, guests={guests}")
        print("=== FUNCTION START ===")
        
        try:
            search_params = {
                "location": city,
                "checkin_date": checkin,
                "checkout_date": checkout,
                "guests": guests,
                "price_min": min_price,
                "price_max": max_price,
                "amenities": amenities
            }
            
            query = self._build_search_query(search_params)

            # Add debug logging
            import json
            logger.info(f"Elasticsearch query: {json.dumps(query, indent=2)}")

            response = self.es.search(
                index=self.index_name,
                body=query,
                size=100  # Return up to 100 hotels
            )
            
            return self._format_search_response(response, search_params)
            
        except Exception as e:
            logger.error(f"Error searching hotels: {e}")
            return {"hotels": [], "total": 0, "error": str(e)}
    
    def _build_search_query(self, params: Dict) -> Dict:
        """Build Elasticsearch query"""
        must_filters = []

        if params.get("location"):
            must_filters.append({
                "match": {
                    "city": {
                        "query": params["location"],
                        "operator": "and"
                    }
                }
            })
        
        # Add rating filter if provided
        if params.get("rating_min"):
            must_filters.append({
                "range": {"current_rating.avg_rating": {"gte": params["rating_min"]}}
            })
        
        # Add price filters if provided (hotel level) - overlap logic
        if params.get("price_min") or params.get("price_max"):
            if params.get("price_min"):
                must_filters.append({
                    "range": {"current_pricing.max_price": {"gte": params["price_min"]}}
                })
            if params.get("price_max"):
                must_filters.append({
                    "range": {"current_pricing.min_price": {"lte": params["price_max"]}}
                })
        
        # Add room type filter if provided
        if params.get("room_type"):
            room_types = params["room_type"] if isinstance(params["room_type"], list) else [params["room_type"]]
            must_filters.append({
                "nested": {
                    "path": "room_types",
                    "query": {
                        "terms": {"room_types.type": room_types}
                    }
                }
            })
        
        # Add occupancy filter if provided
        if params.get("guests"):
            must_filters.append({
                "nested": {
                    "path": "room_types", 
                    "query": {
                        "range": {"room_types.max_occupancy": {"gte": params["guests"]}}
                    }
                }
            })
        
        # Sorting
        sort_order = []
        sort_by = params.get("sort_by", "rating")
        
        if sort_by == "rating":
            sort_order.append({"current_rating.avg_rating": {"order": "desc"}})
        elif sort_by == "price_low":
            sort_order.append({"current_pricing.min_price": {"order": "asc"}})
        elif sort_by == "price_high":
            sort_order.append({"current_pricing.min_price": {"order": "desc"}})
        
        return {
            "query": {"bool": {"must": must_filters}},
            "sort": sort_order
        }
    
    def _format_search_response(self, response: Dict, search_params: Dict) -> Dict:
        """Format Elasticsearch response"""
        hotels = []
        for hit in response["hits"]["hits"]:
            hotel = hit["_source"]
            hotels.append(hotel)
        
        return {
            "hotels": hotels,
            "total": response["hits"]["total"]["value"]
        }
    
    async def get_filters(self, location: str) -> Dict:
        """Get available filters for hotels in a location"""
        try:
            query = {
                "query": {"match": {"city": location}},
                "aggs": {
                    "price_range": {
                        "stats": {"field": "current_pricing.min_price"}
                    },
                    "rating_range": {
                        "stats": {"field": "current_rating.avg_rating"}
                    },
                    "room_types": {
                        "nested": {"path": "room_types"},
                        "aggs": {
                            "types": {
                                "terms": {"field": "room_types.type", "size": 20}
                            }
                        }
                    },
                    "breakfast": {
                        "filter": {"term": {"hotel_amenities.complementary_breakfast": True}}
                    },
                    "parking": {
                        "filter": {"term": {"hotel_amenities.parking_available": True}}
                    },
                    "pets_allowed": {
                        "filter": {"term": {"hotel_policies.pets_allowed": True}}
                    },
                    "wifi": {
                        "filter": {"term": {"hotel_amenities.wifi": True}}
                    },
                    "pool": {
                        "filter": {"term": {"hotel_amenities.pool": True}}
                    },
                    "gym": {
                        "filter": {"term": {"hotel_amenities.gym": True}}
                    },
                    "free_cancellation": {
                        "filter": {"term": {"hotel_policies.free_cancellation": True}}
                    },
                    "no_prepayment": {
                        "filter": {"term": {"hotel_policies.prepayment_needed": False}}
                    }
                }
            }
            
            response = self.es.search(index=self.index_name, body=query, size=0)
            
            return self._format_filters_response(response)
            
        except Exception as e:
            logger.error(f"Error getting filters: {e}")
            return {"error": str(e)}
    
    def _format_filters_response(self, response: Dict) -> Dict:
        """Format filters response"""
        aggs = response["aggregations"]
        
        price_stats = aggs["price_range"]
        rating_stats = aggs["rating_range"]
        
        return {
            "price_range": {
                "min": int(price_stats["min"]) if price_stats["min"] is not None else 0,
                "max": int(price_stats["max"]) if price_stats["max"] is not None else 0
            },
            "rating_range": {
                "min": round(rating_stats["min"], 1) if rating_stats["min"] is not None else 0.0,
                "max": round(rating_stats["max"], 1) if rating_stats["max"] is not None else 0.0
            },
            "room_types": [bucket["key"] for bucket in aggs["room_types"]["types"]["buckets"]],
            "amenities": {
                "breakfast": aggs["breakfast"]["doc_count"],
                "parking": aggs["parking"]["doc_count"],
                "wifi": aggs["wifi"]["doc_count"],
                "pool": aggs["pool"]["doc_count"],
                "gym": aggs["gym"]["doc_count"]
            },
            "policies": {
                "free_cancellation": aggs["free_cancellation"]["doc_count"],
                "no_prepayment": aggs["no_prepayment"]["doc_count"],
                "pets_allowed": aggs["pets_allowed"]["doc_count"]
            }
        }
    
    async def search_cities(self, query: str, limit: int = 10) -> Dict:
        """Search cities by name prefix"""
        try:
            es_query = {
                "query": {
                    "prefix": {
                        "city": query.lower()
                    }
                },
                "aggs": {
                    "unique_cities": {
                        "terms": {
                            "field": "city.keyword",
                            "size": limit
                        }
                    }
                },
                "size": 0
            }
            
            response = self.es.search(
                index=self.index_name,
                body=es_query
            )
            
            cities = [bucket["key"] for bucket in response["aggregations"]["unique_cities"]["buckets"]]
            return {"cities": cities}
            
        except Exception as e:
            logger.error(f"Error searching cities: {e}")
            return {"cities": [], "error": str(e)}
    
    async def get_hotel_by_id(self, hotel_id: str) -> Dict:
        """Get hotel details by ID"""
        try:
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": {"term": {"id": hotel_id}},
                    "size": 1
                }
            )
            
            if response["hits"]["total"]["value"] > 0:
                return {"hotel": response["hits"]["hits"][0]["_source"]}
            else:
                return {"error": f"Hotel {hotel_id} not found"}
            
        except Exception as e:
            logger.error(f"Error getting hotel {hotel_id}: {e}")
            return {"error": f"Hotel {hotel_id} not found"}




















