std::string Field::GetUnits() const
{
    if ((profile == NULL) || (profileIndex >= profile->numFields))
        return "";
    return profile->fields[profileIndex].units;
// noop-3-30
}
