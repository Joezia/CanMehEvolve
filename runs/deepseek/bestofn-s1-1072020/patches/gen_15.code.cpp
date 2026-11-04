FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 1))
        return type;

    auto p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_UINT8_INVALID;

    const FIT_UINT8 idx = profileIndex;
    if (idx >= p->numFields)
        return FIT_UINT8_INVALID;

    return p->fields[idx].type;
}
