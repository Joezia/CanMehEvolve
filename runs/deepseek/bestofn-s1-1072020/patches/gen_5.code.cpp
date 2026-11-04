FIT_FLOAT64 Field::GetOffset() const
{
    if (__builtin_expect((profile == NULL) || (profileIndex >= profile->numFields), 0))
        return 0;
    return profile->fields[profileIndex].offset;
}
