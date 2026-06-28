from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.mysql import get_db
from src.auth.dependencies import get_current_user, require_role
from src.users.models import User, RoleEnum
from src.billing.models import Invoice
from src.billing.schemas import InvoiceCreate, InvoiceUpdate, InvoiceResponse

router = APIRouter()

@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(db: Session = Depends(get_db), _: User = Depends(require_role(RoleEnum.admin))):
    return db.query(Invoice).all()

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    
    if current_user.role != RoleEnum.admin and invoice.client_id != current_user.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
        
    return invoice

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(data: InvoiceCreate, db: Session = Depends(get_db), _: User = Depends(require_role(RoleEnum.admin))):
    new_invoice = Invoice(**data.model_dump())
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice

@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(invoice_id: int, data: InvoiceUpdate, db: Session = Depends(get_db), _: User = Depends(require_role(RoleEnum.admin))):
    invoice = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(invoice, field, value)
        
    db.commit()
    db.refresh(invoice)
    return invoice

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db), _: User = Depends(require_role(RoleEnum.admin))):
    invoice = db.query(Invoice).filter(Invoice.invoice_id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    
    db.delete(invoice)
    db.commit()