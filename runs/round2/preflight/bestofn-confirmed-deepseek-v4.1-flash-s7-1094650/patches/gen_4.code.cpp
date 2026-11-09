FIT_UINT8 Field::GetType() const
{
    const FIT_UINT8 t = type;
    if (__builtin_expect(t != FIT_UINT8_INVALID, 1))
        return t;

    const auto* p = profile;
    if (__builtin_expect(p == nullptr, 0))
        return FIT_UINT8_INVALID;

    const FIT_UINT8 i = profileIndex;
    if (__builtin_expect(i >= p->numFields, 0))
        return FIT_UINT8_INVALID;

    return p->fields[i].type;
}
