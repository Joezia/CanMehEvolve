
FIT_FLOAT64 Field::GetScale() const
{
    return (profile == NULL || profileIndex >= profile->numFields) ? 1.0 : profile->fields[profileIndex].scale;
}
