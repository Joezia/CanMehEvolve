FIT_UINT8 Field::GetType() const
{
    const FIT_UINT8 t = type;
    if (__builtin_expect(t != FIT_UINT8_INVALID, 1))
        return t;

    const Profile* p = profile;
    if (__builtin_expect(p == NULL, 0) || __builtin_expect(profileIndex >= p->numFields, 0))
        return FIT_UINT8_INVALID;

    return p->fields[profileIndex].type;
}
