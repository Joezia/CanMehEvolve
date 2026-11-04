
DeveloperFieldDefinition::~DeveloperFieldDefinition()
{
    delete mesg;
    delete developer;
    mesg = nullptr;
    developer = nullptr;
}
