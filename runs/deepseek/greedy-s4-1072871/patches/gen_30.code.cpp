FIT_FLOAT64 Field::GetOffset() const
{
    const auto p = profile;
    if (__builtin_expect((p == NULL) || (profileIndex >= p->numFields), 0))
        return 0;
    return p->fields[profileIndex].offset;
}
