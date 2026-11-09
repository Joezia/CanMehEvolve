
FIT_FLOAT64 FieldBase::GetOffset(const FIT_UINT16 subFieldIndex) const
{
    if (subFieldIndex >= GetNumSubFields()) return GetOffset();
    auto* subfield = GetSubField(subFieldIndex);
    return subfield ? subfield->offset : 0.0;
}
