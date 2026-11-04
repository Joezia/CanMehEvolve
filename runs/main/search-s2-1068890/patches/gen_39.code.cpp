
FIT_BOOL FieldBase::IsSignedInteger(const FIT_UINT16 subFieldIndex) const
{
    FIT_BASE_TYPE type = GetType(subFieldIndex);
    // Signed integers: SINT8(4), SINT16(5), SINT32(6) -> check if type is in [4,6]
    return (static_cast<uint8_t>(type) - 4U) <= 2U ? FIT_TRUE : FIT_FALSE;
}
