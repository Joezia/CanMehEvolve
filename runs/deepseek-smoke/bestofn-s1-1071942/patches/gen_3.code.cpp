FIT_BOOL Field::IsValid(void) const
{
    return static_cast<FIT_BOOL>(profileIndex != FIT_UINT16_INVALID);
}
