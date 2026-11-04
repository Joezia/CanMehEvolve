FIT_UINT8 Field::GetType() const
{
    const FIT_UINT8 t = type;
    if (t != FIT_UINT8_INVALID)
        return t;

    const auto* p = profile;
    if (__builtin_expect(p == 0, 0) || profileIndex >= p->numFields)
        return FIT_UINT8_INVALID;

    return p->fields[profileIndex].type;
}
