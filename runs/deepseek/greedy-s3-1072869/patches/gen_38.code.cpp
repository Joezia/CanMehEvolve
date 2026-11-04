FIT_BYTE FieldBase::GetValuesBYTE(FIT_UINT8 index) const
{
    return (index < size) ? values[index] : FIT_BYTE_INVALID;
}
