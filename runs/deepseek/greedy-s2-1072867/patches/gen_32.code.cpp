FIT_FLOAT64 FieldBase::GetScale(const FIT_UINT16 subFieldIndex) const
{
    const FIT_SUBFIELD_INFO *subfield = GetSubField(subFieldIndex);
    return (NULL != subfield) ? subfield->scale : GetScale();
}
