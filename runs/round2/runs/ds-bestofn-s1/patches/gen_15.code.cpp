FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 1))
        return type;

    const auto* p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_UINT8_INVALID;

    const auto idx = profileIndex;
    if (__builtin_expect(idx >= p->numFields, 0))
        return FIT_UINT8_INVALID;

    return p->fields[idx].type;
}
