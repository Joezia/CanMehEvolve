
FIT_BOOL FieldBase::IsSignedInteger(const FIT_UINT16 subFieldIndex) const
{
    FIT_BASE_TYPE type = static_cast<FIT_BASE_TYPE>(GetType(subFieldIndex));
    // Efficient range check: signed integers are 0x04 (SINT8), 0x05 (SINT16), 0x06 (SINT32)
    return (type == FIT_BASE_TYPE_SINT8 || type == FIT_BASE_TYPE_SINT16 || type == FIT_BASE_TYPE_SINT32) ? FIT_TRUE : FIT_FALSE;
}
