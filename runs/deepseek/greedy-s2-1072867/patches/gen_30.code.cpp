FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 t = type;
    if (__builtin_expect(t != FIT_UINT8_INVALID, 0))
        return t;

    const Profile* p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_UINT8_INVALID;

    FIT_UINT16 idx = profileIndex;
    if (__builtin_expect(idx >= p->numFields, 0))
        return FIT_UINT8_INVALID;

    return p->fields[idx].type;
}
