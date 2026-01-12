"""
Reusable UI components for the frontend.
"""

from typing import List, Dict, Any, Optional


class UIComponents:
    """Collection of reusable UI components."""

    @staticmethod
    def format_diagnosis_card(diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format diagnosis data for display as a card.
        
        Args:
            diagnosis: Diagnosis data
            
        Returns:
            Formatted card data
        """
        return {
            "title": f"Diagnosis #{diagnosis.get('id', 'N/A')}",
            "status": diagnosis.get("status", "unknown"),
            "date": diagnosis.get("created_at", ""),
            "confidence": diagnosis.get("confidence_score", 0),
            "animal": diagnosis.get("animal", {}),
        }

    @staticmethod
    def format_animal_info(animal: Dict[str, Any]) -> str:
        """
        Format animal information for display.
        
        Args:
            animal: Animal data
            
        Returns:
            Formatted string
        """
        parts = [animal.get("name", "Unknown")]
        
        if animal.get("species"):
            parts.append(animal["species"])
        
        if animal.get("breed"):
            parts.append(animal["breed"])
        
        if animal.get("age"):
            parts.append(f"{animal['age']} years old")
        
        return " - ".join(parts)

    @staticmethod
    def create_status_badge(status: str) -> Dict[str, str]:
        """
        Create a status badge configuration.
        
        Args:
            status: Status value
            
        Returns:
            Badge configuration
        """
        status_colors = {
            "pending": "orange",
            "in_progress": "blue",
            "completed": "green",
            "reviewed": "purple",
            "archived": "gray",
            "active": "green",
            "cancelled": "red",
            "expired": "gray",
        }
        
        return {
            "text": status.replace("_", " ").title(),
            "color": status_colors.get(status.lower(), "gray"),
        }

    @staticmethod
    def format_confidence_score(score: float) -> Dict[str, Any]:
        """
        Format confidence score with color coding.
        
        Args:
            score: Confidence score (0-1)
            
        Returns:
            Formatted score data
        """
        percentage = score * 100
        
        if percentage >= 80:
            color = "green"
            label = "High"
        elif percentage >= 60:
            color = "orange"
            label = "Moderate"
        else:
            color = "red"
            label = "Low"
        
        return {
            "value": percentage,
            "label": label,
            "color": color,
            "display": f"{percentage:.1f}%",
        }

    @staticmethod
    def create_breadcrumb(items: List[str]) -> List[Dict[str, str]]:
        """
        Create breadcrumb navigation.
        
        Args:
            items: List of breadcrumb items
            
        Returns:
            Breadcrumb configuration
        """
        return [
            {"text": item, "index": i}
            for i, item in enumerate(items)
        ]

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def create_pagination(
        current_page: int,
        total_pages: int,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Create pagination configuration.
        
        Args:
            current_page: Current page number (1-indexed)
            total_pages: Total number of pages
            page_size: Items per page
            
        Returns:
            Pagination configuration
        """
        return {
            "current_page": current_page,
            "total_pages": total_pages,
            "page_size": page_size,
            "has_previous": current_page > 1,
            "has_next": current_page < total_pages,
            "previous_page": max(1, current_page - 1),
            "next_page": min(total_pages, current_page + 1),
        }

    @staticmethod
    def format_timestamp(timestamp: str, format: str = "friendly") -> str:
        """
        Format timestamp for display.
        
        Args:
            timestamp: ISO format timestamp
            format: Display format ('friendly', 'date', 'datetime')
            
        Returns:
            Formatted timestamp
        """
        from datetime import datetime
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if format == "friendly":
                # Return relative time
                now = datetime.utcnow()
                diff = now - dt
                
                if diff.days > 365:
                    return f"{diff.days // 365} year(s) ago"
                elif diff.days > 30:
                    return f"{diff.days // 30} month(s) ago"
                elif diff.days > 0:
                    return f"{diff.days} day(s) ago"
                elif diff.seconds > 3600:
                    return f"{diff.seconds // 3600} hour(s) ago"
                elif diff.seconds > 60:
                    return f"{diff.seconds // 60} minute(s) ago"
                else:
                    return "Just now"
            elif format == "date":
                return dt.strftime("%Y-%m-%d")
            elif format == "datetime":
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return timestamp
        except Exception:
            return timestamp

    @staticmethod
    def create_alert(
        message: str,
        alert_type: str = "info",
        dismissible: bool = True
    ) -> Dict[str, Any]:
        """
        Create alert configuration.
        
        Args:
            message: Alert message
            alert_type: Type of alert ('info', 'success', 'warning', 'error')
            dismissible: Whether alert can be dismissed
            
        Returns:
            Alert configuration
        """
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
        }
        
        return {
            "message": message,
            "type": alert_type,
            "icon": icons.get(alert_type, "ℹ️"),
            "dismissible": dismissible,
        }


# Export singleton instance
ui_components = UIComponents()
