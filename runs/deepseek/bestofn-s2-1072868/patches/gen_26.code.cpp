FIT_BOOL Field::IsValid(void) const
{
    return __builtin_expect(profileIndex != FIT_UINT16_INVALID, 1);
}
