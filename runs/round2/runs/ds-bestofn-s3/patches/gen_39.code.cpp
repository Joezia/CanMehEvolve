Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    if (!fields.empty())
    {
        Field* field = &fields[0];
        Field* const end = field + fields.size();

        do
        {
            if (field->GetNum() == fieldNum)
                return field;
            ++field;
        } while (field != end);
    }

    return FIT_NULL;
}
