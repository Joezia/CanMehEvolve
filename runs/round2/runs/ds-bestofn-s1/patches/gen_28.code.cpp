FIT_UINT8 Field::GetType() const
{
    if (type != FIT_UINT8_INVALID)
        return type;

    const Profile* const p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_UINT8_INVALID;

    const auto index = profileIndex;
    if (__builtin_expect(index >= p->numFields, 0))
        return FIT_UINT8_INVALID;

    return p->fields[index].type;
}
