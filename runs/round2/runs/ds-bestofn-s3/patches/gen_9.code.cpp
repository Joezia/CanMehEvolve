FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 0))
        return type;

    const Profile* p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_UINT8_INVALID;

    const FIT_UINT8 idx = profileIndex;
    if (__builtin_expect(idx >= p->numFields, 0))
        return FIT_UINT8_INVALID;

    return p->fields[idx].type;
}
