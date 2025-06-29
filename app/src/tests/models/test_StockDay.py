import pytest
from datetime import date
from django.db import IntegrityError
from products.models import StockDay


@pytest.mark.django_db
class TestStockDay:
    
    def test_create_stock_day(self):
        """Test creación de stock day"""
        stock_date = date(2024, 1, 15)
        stock_day = StockDay.objects.create(date=stock_date)
        assert stock_day.date == stock_date
        assert stock_day.is_active is True  # BaseModel default
        
    def test_unique_date_constraint(self):
        """Test restricción unique del campo date"""
        stock_date = date(2024, 1, 15)
        StockDay.objects.create(date=stock_date)
        
        with pytest.raises(IntegrityError):
            StockDay.objects.create(date=stock_date)
            
    def test_get_stock_day_method(self):
        """Test método get_stock_day"""
        stock_date = date(2024, 1, 15)
        stock_day = StockDay.objects.create(date=stock_date)
        
        # Test encontrar stock existente usando método de clase
        found_stock = StockDay.get_stock_day(stock_date)
        assert found_stock == stock_day
        
        # Test no encontrar stock
        non_existent_date = date(2024, 2, 15)
        not_found = StockDay.get_stock_day(non_existent_date)
        assert not_found is None
        
    def test_disable_classmethod(self):
        """Test método classmethod disable"""
        stock_day = StockDay.objects.create(date=date(2024, 1, 15))
        assert stock_day.is_active is True
        
        StockDay.disable(stock_day)
        stock_day.refresh_from_db()
        assert stock_day.is_active is False
        
    def test_get_by_id_classmethod(self):
        """Test método classmethod get_by_id"""
        stock_day = StockDay.objects.create(date=date(2024, 1, 15))
        
        # Test encontrar por ID existente
        found_stock = StockDay.get_by_id(stock_day.id)
        assert found_stock == stock_day
        
        # Test ID no existente
        with pytest.raises(Exception) as exc_info:
            StockDay.get_by_id(99999)
        assert "Registro de stock Eliminado" in str(exc_info.value)
        
    def test_get_by_id_deleted_record(self):
        """Test get_by_id con registro eliminado"""
        stock_day = StockDay.objects.create(date=date(2024, 1, 15))
        stock_id = stock_day.id
        # Usar método de queryset en lugar del método personalizado
        StockDay.objects.filter(id=stock_id).delete()
        
        with pytest.raises(Exception) as exc_info:
            StockDay.get_by_id(stock_id)
        assert "Registro de stock Eliminado" in str(exc_info.value)
        
    def test_str_method(self):
        """Test método __str__"""
        stock_date = date(2024, 1, 15)
        stock_day = StockDay.objects.create(date=stock_date)
        assert str(stock_day) == "2024-01-15"
        
    def test_auto_field_id(self):
        """Test que el ID es auto generado"""
        stock_day = StockDay.objects.create(date=date(2024, 1, 15))
        assert stock_day.id is not None
        assert isinstance(stock_day.id, int)
        assert stock_day.id > 0
        
    def test_base_model_inheritance(self):
        """Test herencia de BaseModel"""
        stock_day = StockDay.objects.create(date=date(2024, 1, 15))
        
        # Verificar que tiene los campos de BaseModel
        assert hasattr(stock_day, 'is_active')
        assert hasattr(stock_day, 'created_at')
        assert hasattr(stock_day, 'updated_at')
        
        # Verificar valores por defecto de BaseModel
        assert stock_day.is_active is True
        assert stock_day.created_at is not None
        assert stock_day.updated_at is not None
