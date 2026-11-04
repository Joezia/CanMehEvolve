FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 1))
        return type;

    if (__builtin_expect(profile == NULL, 0))
        return FIT_UINT8_INVALID;

    if (__builtin_expect(profileIndex >= profile->numFields, 0))
        return FIT_UINT8_INVALID;

    return profile->fields[profileIndex].type;
}
