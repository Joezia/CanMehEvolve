FIT_FLOAT64 Field::GetScale() const
{
    if (__builtin_expect((profile == NULL) || (profileIndex >= profile->numFields), 0))
        return 1;
    return profile->fields[profileIndex].scale;
}
