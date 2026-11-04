FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 1))
        return type;

    const Profile* const p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_UINT8_INVALID;

    const auto idx = profileIndex;
    const auto num = p->numFields;
    const auto fields = p->fields;
    if (__builtin_expect(idx >= num, 0))
        return FIT_UINT8_INVALID;

    return fields[idx].type;
}
