FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 t = type;
    if (__builtin_expect(t != FIT_UINT8_INVALID, 1))
        return t;

    const Profile* p = profile;
    if (__builtin_expect(p != NULL, 1))
    {
        FIT_UINT8 idx = profileIndex;
        if (__builtin_expect(idx < p->numFields, 1))
            return p->fields[idx].type;
    }

    return FIT_UINT8_INVALID;
}
