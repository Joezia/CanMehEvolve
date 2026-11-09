
FIT_BOOL FieldBase::IsSignedInteger(const FIT_UINT16 subFieldIndex) const
{
    const FIT_BASE_TYPE type = static_cast<FIT_BASE_TYPE>(GetType(subFieldIndex));
    // Signed integers are contiguous: SINT8=2, SINT16=3, SINT32=4
    return (type >= FIT_BASE_TYPE_SINT8 && type <= FIT_BASE_TYPE_SINT32) ? FIT_TRUE : FIT_FALSE;
}
