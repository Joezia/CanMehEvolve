FIT_UINT8 Field::GetType() const
{
    const FIT_UINT8 cachedType = type;
    if (__builtin_expect(cachedType != FIT_UINT8_INVALID, 1))
        return cachedType;

    const Profile::MESG* const p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_UINT8_INVALID;

    const FIT_UINT8 index = profileIndex;
    if (__builtin_expect(index >= p->numFields, 0))
        return FIT_UINT8_INVALID;

    return p->fields[index].type;
}
