import React from 'react';
import PropTypes from 'prop-types';
import {withRouter} from 'react-router';
import styled from 'react-emotion';
import {Flex, Box} from 'grid-emotion';
import moment from 'moment-timezone';

import SentryTypes from 'app/proptypes';
import Button from 'app/components/buttons/button';
import Link from 'app/components/link';
import {t} from 'app/locale';
import TextOverflow from 'app/components/textOverflow';

const DEPLOY_COUNT = 2;

class Deploys extends React.Component {
  static propTypes = {
    project: SentryTypes.Project,
  };

  render() {
    const {project, params} = this.props;

    const projectId = project.slug;

    const deploys = (project.latestDeploys || [])
      .sort((a, b) => new Date(b.dateFinished) - new Date(a.dateFinished))
      .slice(0, DEPLOY_COUNT);

    if (deploys.length) {
      return (
        <StyledDeploys p={2} pb={0}>
          <Heading>{t('Latest deploys')}</Heading>
          <div>
            {deploys.map(deploy => (
              <Deploy
                key={deploy.version}
                deploy={deploy}
                projectId={projectId}
                orgId={params.orgId}
              />
            ))}
          </div>
        </StyledDeploys>
      );
    } else {
      return <NoDeploys />;
    }
  }
}

const Heading = styled.div`
  color: ${p => p.theme.gray2};
  text-transform: uppercase;
  font-size: 14px;
`;

class Deploy extends React.Component {
  static propTypes = {
    deploy: PropTypes.object.isRequired,
    projectId: PropTypes.string.isRequired,
    orgId: PropTypes.string.isRequired,
  };

  render() {
    const {deploy, orgId, projectId} = this.props;
    return (
      <DeployRow justify="space-between">
        <Flex flex="1">
          <Environment>{deploy.environment}</Environment>
          <Flex>
            <Link to={`/${orgId}/${projectId}/releases/${deploy.version}/`}>
              {deploy.version}
            </Link>
          </Flex>
        </Flex>
        <Box w={80}>{moment(deploy.dateFinished).fromNow()}</Box>
      </DeployRow>
    );
  }
}

const DeployRow = styled(Flex)`
  color: ${p => p.theme.gray2};
  font-size: 13px;
  margin-top: 8px;
`;

const Environment = styled(TextOverflow)`
  font-size: 11px;
  text-transform: uppercase;
  width: 80px;
  border: 1px solid ${p => p.theme.offWhite2};
  margin-right: 8px;
  background-color: ${p => p.theme.offWhite};
  text-align: center;
  border-radius: ${p => p.theme.borderRadius};
`;

class NoDeploys extends React.Component {
  render() {
    return (
      <StyledDeploys p={2} pb={0}>
        <Background align="center" justify="center">
          <Button size="xsmall" href="https://blog.sentry.io/2017/05/09/release-deploys">
            {t('Track deploys')}
          </Button>
        </Background>
      </StyledDeploys>
    );
  }
}

const StyledDeploys = styled(Box)`
  height: 108px;
`;

const Background = styled(Flex)`
  height: 100%;
  background-color: ${p => p.theme.offWhite};
`;

export default withRouter(Deploys);
