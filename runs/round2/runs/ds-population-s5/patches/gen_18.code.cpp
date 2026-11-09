FIT_FLOAT64 FieldBase::GetScale(const FIT_UINT16 subFieldIndex) const
{
    if (subFieldIndex < GetNumSubFields())
        return GetSubField(subFieldIndex)->scale;

    return GetScale();
}
