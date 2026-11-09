FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 t = type;
    if (__builtin_expect(t == FIT_UINT8_INVALID, 0))
    {
        const auto p = profile;
        if (p != NULL && profileIndex < p->numFields)
            t = p->fields[profileIndex].type;
    }
    return t;
}
