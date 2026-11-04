FIT_UINT8 Field::GetType() const
{
    const FIT_UINT8 t = type;
    if (__builtin_expect(t != FIT_UINT8_INVALID, 1))
        return t;

    const auto p = profile;
    const auto idx = profileIndex;
    if (__builtin_expect(p != NULL && idx < p->numFields, 1))
        return p->fields[idx].type;

    return FIT_UINT8_INVALID;
}
