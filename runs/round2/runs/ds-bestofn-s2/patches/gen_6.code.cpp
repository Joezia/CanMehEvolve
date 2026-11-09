FIT_UINT8 FieldBase::GetSize(void) const
{
    return __builtin_expect(IsValid(), 1) ? (FIT_UINT8)values.size() : (FIT_UINT8)0;
}
