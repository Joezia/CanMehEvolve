FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 1))
        return type;

    if (profile != NULL && profileIndex < profile->numFields)
        return profile->fields[profileIndex].type;

    return FIT_UINT8_INVALID;
}
