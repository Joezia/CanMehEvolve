FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 t = type;
    if (__builtin_expect(t != FIT_UINT8_INVALID, 1))
        return t;

    if (__builtin_expect(profile != NULL && profileIndex < profile->numFields, 1))
        return profile->fields[profileIndex].type;

    return t;
}
