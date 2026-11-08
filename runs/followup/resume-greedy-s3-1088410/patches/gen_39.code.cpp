Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    const auto count = fields.size();
    if (count == 0)
        return FIT_NULL;

    Field* field = fields.data();
    Field* const end = field + count;

    for (; field != end; ++field)
    {
        if (field->GetNum() == fieldNum)
            return field;
    }

    return FIT_NULL;
}
