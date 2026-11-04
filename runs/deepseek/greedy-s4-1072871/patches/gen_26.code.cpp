FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type == FIT_UINT8_INVALID, 1))
    {
        const auto p = profile;
        if ((p != NULL) && (profileIndex < p->numFields))
            return p->fields[profileIndex].type;
    }

    return type;
}
