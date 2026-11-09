FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 result = type;
    if (__builtin_expect(result == FIT_UINT8_INVALID, 0))
    {
        if (__builtin_expect(profile != NULL, 1) &&
            __builtin_expect(profileIndex < profile->numFields, 1))
        {
            result = profile->fields[profileIndex].type;
        }
    }
    return result;
}
